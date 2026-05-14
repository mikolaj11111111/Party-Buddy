import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from secrets import SystemRandom
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from backend.app.core.answer_service import QUESTIONS_DIRECTORY
from backend.app.core.game_comments import (
    GameComment,
    get_answer_comment,
    get_intro_comment,
    get_outro_comment,
)
from backend.app.core.game_engine import (
    GameAnswerRecord,
    GameEngineError,
    GamePlayer,
    GameSessionState,
    create_game_session,
)
from backend.app.core.question_loader import (
    QuestionLoaderError,
    load_questions_from_directory,
)
from backend.app.models.game_ws import (
    GameAnswerResultEvent,
    GameClientMessage,
    GameErrorEvent,
    GameInputMethod,
    GamePlayerPayload,
    GameQuestionPayload,
    GameRoundStartedEvent,
    GameScorePayload,
    GameServerEvent,
    GameSessionFinishedEvent,
    GameSessionStartedEvent,
    GameStartSessionMessage,
    GameSubmitAnswerMessage,
)
from backend.app.models.question import AnswerLetter, Question
from backend.app.models.timestamps import utc_now

QUESTION_RANDOM = SystemRandom()


class GameProtocolError(ValueError):
    """Raised when a WebSocket client sends an invalid game message."""

    def __init__(self, message: str, code: str = "bad_message") -> None:
        """Store a stable error code next to the client-facing message."""

        super().__init__(message)
        self.code = code


class GameSessionController:
    """Owns one in-memory game session and converts messages into events."""

    def __init__(
        self,
        questions: list[Question],
        *,
        now: Callable[[], datetime] = utc_now,
        shuffle_questions: bool = True,
    ) -> None:
        """Prepare a controller with the question pool for one connection."""

        self._questions = questions
        self._now = now
        self._shuffle_questions = shuffle_questions
        self._session: GameSessionState | None = None
        self._deadline_at: datetime | None = None

    def handle_payload(self, payload: Any) -> list[GameServerEvent]:
        """Parse one client payload and return resulting server events."""

        message = parse_game_client_message(payload)
        if isinstance(message, GameStartSessionMessage):
            return self.start_session(message)

        return self.submit_answer(message)

    def start_session(self, message: GameStartSessionMessage) -> list[GameServerEvent]:
        """Create a new session and emit the first round."""

        if self._session is not None and self._session.status == "in_progress":
            raise GameProtocolError(
                "game session is already in progress",
                code="session_in_progress",
            )

        selected_questions = self._select_questions(
            categories=message.categories,
            round_count=message.round_count,
        )
        self._session = create_game_session(
            player_names=message.players,
            questions=selected_questions,
            round_count=message.round_count,
            round_seconds=message.round_seconds,
        )

        return [
            self._build_session_started_event(),
            self._build_round_started_event(comment=get_intro_comment()),
        ]

    def submit_answer(
        self,
        message: GameSubmitAnswerMessage,
    ) -> list[GameServerEvent]:
        """Judge a submitted answer or resolve the round as timed out."""

        session = self._require_active_session()
        question = session.current_question
        if question is None:
            raise GameProtocolError("game session has no active question")

        if question.id != message.question_id:
            raise GameProtocolError(
                "submitted question is not active",
                code="inactive_question",
            )

        if self._is_deadline_expired():
            return self.handle_round_timeout()

        try:
            answer_record = session.submit_answer(
                answer_letter=message.answer_letter,
                answer_text=message.answer_text,
            )
        except (GameEngineError, ValueError) as error:
            raise GameProtocolError(str(error)) from error

        return self._build_answer_events(
            answer_record,
            input_method=message.input_method,
            timed_out=False,
        )

    def handle_round_timeout(self) -> list[GameServerEvent]:
        """Resolve the active round as timeout if its deadline passed."""

        session = self._require_active_session()
        if not self._is_deadline_expired():
            return []

        try:
            answer_record = session.submit_timeout()
        except GameEngineError as error:
            raise GameProtocolError(str(error)) from error

        return self._build_answer_events(
            answer_record,
            input_method="timeout",
            timed_out=True,
        )

    def seconds_until_deadline(self) -> float | None:
        """Return seconds until active deadline, or None when idle/finished."""

        if self._session is None or self._session.status == "finished":
            return None

        if self._deadline_at is None:
            return None

        return max((self._deadline_at - self._now()).total_seconds(), 0.0)

    def _select_questions(
        self,
        *,
        categories: list[str] | None,
        round_count: int,
    ) -> list[Question]:
        """Filter and optionally shuffle questions for the requested session."""

        questions = self._questions
        if categories is not None:
            category_filter = {category.lower() for category in categories}
            questions = [
                question
                for question in questions
                if question.category.lower() in category_filter
            ]

        if len(questions) < round_count:
            raise GameProtocolError(
                "not enough questions for requested session",
                code="not_enough_questions",
            )

        selected_questions = list(questions)
        if self._shuffle_questions:
            QUESTION_RANDOM.shuffle(selected_questions)

        return selected_questions

    def _require_active_session(self) -> GameSessionState:
        """Return the active session or raise a protocol error."""

        if self._session is None:
            raise GameProtocolError("game session has not started", code="no_session")

        if self._session.status == "finished":
            raise GameProtocolError(
                "game session is already finished",
                code="session_finished",
            )

        return self._session

    def _is_deadline_expired(self) -> bool:
        """Check whether the active round deadline has passed."""

        return self._deadline_at is not None and self._now() >= self._deadline_at

    def _build_session_started_event(self) -> GameSessionStartedEvent:
        """Build the event confirming session creation."""

        session = self._require_session()
        return GameSessionStartedEvent(
            session_id=session.session_id,
            players=[_to_player_payload(player) for player in session.players],
            round_count=session.round_count,
            round_seconds=session.round_seconds,
            scoreboard=self._scoreboard(),
        )

    def _build_round_started_event(
        self,
        comment: GameComment | None = None,
    ) -> GameRoundStartedEvent:
        """Build the event that exposes the active question and deadline."""

        session = self._require_active_session()
        question = session.current_question
        player = session.current_player
        if question is None or player is None:
            raise GameProtocolError("game session has no active turn")

        self._deadline_at = self._now() + timedelta(seconds=session.round_seconds)
        return GameRoundStartedEvent(
            session_id=session.session_id,
            round_number=session.current_round_number,
            active_player=_to_player_payload(player),
            question=_to_question_payload(question),
            deadline_at=self._deadline_at,
            scoreboard=self._scoreboard(),
            comment_id=comment.id if comment else None,
            comment_key=comment.key if comment else None,
        )

    def _build_answer_events(
        self,
        answer_record: GameAnswerRecord,
        *,
        input_method: GameInputMethod,
        timed_out: bool,
    ) -> list[GameServerEvent]:
        """Build result and follow-up events after one round is resolved."""

        session = self._require_session()
        self._deadline_at = None
        answer_comment = get_answer_comment(
            is_correct=answer_record.is_correct,
            round_number=answer_record.round_number,
        )
        events: list[GameServerEvent] = [
            GameAnswerResultEvent(
                session_id=session.session_id,
                round_number=answer_record.round_number,
                player=GamePlayerPayload(
                    player_id=answer_record.player_id,
                    player_name=answer_record.player_name,
                ),
                question_id=answer_record.question_id,
                input_method=input_method,
                submitted_answer=answer_record.submitted_answer,
                matched_answer=answer_record.matched_answer,
                is_correct=answer_record.is_correct,
                correct_answer=answer_record.correct_answer,
                explanation=answer_record.explanation,
                score_delta=answer_record.score_delta,
                timed_out=timed_out,
                scoreboard=self._scoreboard(),
                comment_id=answer_comment.id,
                comment_key=answer_comment.key,
            )
        ]

        if session.status == "finished":
            events.append(self._build_session_finished_event())
        else:
            events.append(self._build_round_started_event())

        return events

    def _build_session_finished_event(self) -> GameSessionFinishedEvent:
        """Build the final scoreboard event after all rounds finish."""

        session = self._require_session()
        scoreboard = self._scoreboard()
        top_score = scoreboard[0].score if scoreboard else 0
        winners = [score for score in scoreboard if score.score == top_score]
        comment = get_outro_comment()
        return GameSessionFinishedEvent(
            session_id=session.session_id,
            scoreboard=scoreboard,
            winners=winners,
            comment_id=comment.id,
            comment_key=comment.key,
        )

    def _scoreboard(self) -> list[GameScorePayload]:
        """Return the current scoreboard as public payload rows."""

        session = self._require_session()
        return [
            GameScorePayload(
                player_id=score.player_id,
                player_name=score.player_name,
                score=score.score,
            )
            for score in session.get_scoreboard()
        ]

    def _require_session(self) -> GameSessionState:
        """Return the current session, including a finished one."""

        if self._session is None:
            raise GameProtocolError("game session has not started", code="no_session")

        return self._session


class GameWebSocketConnection:
    """Coordinates WebSocket I/O for one active game connection."""

    def __init__(
        self,
        questions_directory: Path = QUESTIONS_DIRECTORY,
        *,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        """Store dependencies needed by the connection handler."""

        self._questions_directory = questions_directory
        self._now = now

    async def run(self, websocket: WebSocket) -> None:
        """Accept a WebSocket and run the game message loop."""

        await websocket.accept()

        try:
            questions = load_questions_from_directory(self._questions_directory)
        except QuestionLoaderError as error:
            await _send_event(
                websocket,
                GameErrorEvent(code="question_loader_error", message=str(error)),
            )
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            return

        controller = GameSessionController(questions, now=self._now)
        while True:
            try:
                payload = await _receive_payload(websocket, controller)
                events = controller.handle_payload(payload)
            except TimeoutError:
                events = _handle_timeout(controller)
            except WebSocketDisconnect:
                return
            except GameProtocolError as error:
                events = [GameErrorEvent(code=error.code, message=str(error))]
            except ValueError as error:
                events = [GameErrorEvent(code="bad_json", message=str(error))]

            await _send_events(websocket, events)


def parse_game_client_message(payload: Any) -> GameClientMessage:
    """Validate a raw WebSocket payload into a known client message."""

    if not isinstance(payload, dict):
        raise GameProtocolError("message must be a JSON object")

    message_type = payload.get("type")
    try:
        if message_type == "start_session":
            return GameStartSessionMessage.model_validate(payload)

        if message_type == "submit_answer":
            return GameSubmitAnswerMessage.model_validate(payload)
    except ValidationError as error:
        raise GameProtocolError(_format_validation_error(error)) from error

    raise GameProtocolError("unsupported message type", code="unsupported_type")


def _handle_timeout(controller: GameSessionController) -> list[GameServerEvent]:
    """Resolve timeout errors without crashing the WebSocket loop."""

    try:
        return controller.handle_round_timeout()
    except GameProtocolError as error:
        return [GameErrorEvent(code=error.code, message=str(error))]


async def _receive_payload(
    websocket: WebSocket,
    controller: GameSessionController,
) -> Any:
    """Receive JSON while respecting the active round deadline."""

    timeout = controller.seconds_until_deadline()
    if timeout is None:
        return await websocket.receive_json()

    return await asyncio.wait_for(websocket.receive_json(), timeout=timeout)


async def _send_events(
    websocket: WebSocket,
    events: list[GameServerEvent],
) -> None:
    """Send all events in order over the WebSocket."""

    for event in events:
        await _send_event(websocket, event)


async def _send_event(websocket: WebSocket, event: GameServerEvent) -> None:
    """Serialize and send one server event."""

    await websocket.send_json(event.model_dump(mode="json"))


def _to_player_payload(player: GamePlayer) -> GamePlayerPayload:
    """Convert an internal player to its public payload."""

    return GamePlayerPayload(player_id=player.id, player_name=player.name)


def _to_question_payload(question: Question) -> GameQuestionPayload:
    """Convert a full question into the safe frontend payload."""

    return GameQuestionPayload(
        id=question.id,
        category=question.category,
        difficulty=str(question.difficulty),
        question=question.question,
        options={
            _answer_letter_to_text(letter): option
            for letter, option in question.options.items()
        },
    )


def _answer_letter_to_text(letter: AnswerLetter | str) -> str:
    """Return a stable ABCD string for enum or plain string keys."""

    return letter.value if isinstance(letter, AnswerLetter) else str(letter)


def _format_validation_error(error: ValidationError) -> str:
    """Keep Pydantic validation errors short enough for WebSocket clients."""

    first_error = error.errors()[0]
    location = ".".join(str(part) for part in first_error.get("loc", ()))
    message = str(first_error.get("msg", "invalid message"))
    return f"{location}: {message}" if location else message
