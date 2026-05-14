from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

from backend.app.core.judge import JudgeResult, judge_answer
from backend.app.models.question import AnswerLetter, Question

DEFAULT_ROUND_COUNT = 10
DEFAULT_ROUND_SECONDS = 15
MAX_PLAYERS = 6

GameStatus = Literal["in_progress", "finished"]


class GameEngineError(ValueError):
    """Raised when a game session cannot be created or advanced."""

    pass


@dataclass(frozen=True)
class GamePlayer:
    """One local solo or hotseat player participating in a session."""

    id: str
    name: str


@dataclass(frozen=True)
class PlayerScore:
    """Current score row for one player in the session ranking."""

    player_id: str
    player_name: str
    score: int


@dataclass(frozen=True)
class GameAnswerRecord:
    """Stored result of one player answering one queued question."""

    round_number: int
    player_id: str
    player_name: str
    question_id: str
    submitted_answer: str
    matched_answer: AnswerLetter | None
    is_correct: bool
    correct_answer: AnswerLetter
    explanation: str | None
    score_delta: int


@dataclass
class GameSessionState:
    """Mutable in-memory state for one trivia session."""

    session_id: str
    players: tuple[GamePlayer, ...]
    question_queue: tuple[Question, ...]
    round_seconds: int = DEFAULT_ROUND_SECONDS
    current_question_index: int = 0
    current_player_index: int = 0
    scores: dict[str, int] = field(default_factory=dict)
    answer_history: list[GameAnswerRecord] = field(default_factory=list)
    status: GameStatus = "in_progress"

    def __post_init__(self) -> None:
        """Initialize missing score entries for all players."""

        for player in self.players:
            self.scores.setdefault(player.id, 0)

    @property
    def round_count(self) -> int:
        """Return the number of questions scheduled for this session."""

        return len(self.question_queue)

    @property
    def current_round_number(self) -> int:
        """Return the active round number using one-based numbering."""

        if self.status == "finished":
            return self.round_count

        return self.current_question_index + 1

    @property
    def current_question(self) -> Question | None:
        """Return the active question or None after the session ends."""

        if self.status == "finished":
            return None

        return self.question_queue[self.current_question_index]

    @property
    def current_player(self) -> GamePlayer | None:
        """Return the player whose turn is active or None after finish."""

        if self.status == "finished":
            return None

        return self.players[self.current_player_index]

    @property
    def remaining_questions(self) -> int:
        """Return how many questions have not been answered yet."""

        return self.round_count - len(self.answer_history)

    def submit_answer(
        self,
        *,
        answer_letter: str | None = None,
        answer_text: str | None = None,
    ) -> GameAnswerRecord:
        """Judge the active player's answer, update score, and advance turn."""

        if self.status == "finished":
            raise GameEngineError("game session is already finished")

        question = self.current_question
        player = self.current_player
        if question is None or player is None:
            raise GameEngineError("game session has no active turn")

        judge_result = judge_answer(
            question,
            answer_letter=answer_letter,
            answer_text=answer_text,
        )
        self.scores[player.id] += judge_result.score_delta

        answer_record = _build_answer_record(
            self.current_round_number,
            player,
            judge_result,
        )
        self.answer_history.append(answer_record)
        self._advance_turn()
        return answer_record

    def get_scoreboard(self) -> list[PlayerScore]:
        """Return players ordered by score descending and original turn order."""

        player_order = {player.id: index for index, player in enumerate(self.players)}
        scores = [
            PlayerScore(
                player_id=player.id,
                player_name=player.name,
                score=self.scores[player.id],
            )
            for player in self.players
        ]
        return sorted(
            scores,
            key=lambda score: (-score.score, player_order[score.player_id]),
        )

    def _advance_turn(self) -> None:
        """Move to the next question and rotate the active hotseat player."""

        next_question_index = self.current_question_index + 1
        if next_question_index >= self.round_count:
            self.status = "finished"
            self.current_question_index = self.round_count
            return

        self.current_question_index = next_question_index
        self.current_player_index = (self.current_player_index + 1) % len(self.players)


def create_game_session(
    *,
    player_names: list[str],
    questions: list[Question],
    round_count: int = DEFAULT_ROUND_COUNT,
    round_seconds: int = DEFAULT_ROUND_SECONDS,
    session_id: str | None = None,
) -> GameSessionState:
    """Create an in-memory session with a fixed question queue."""

    players = _build_players(player_names)
    question_queue = _build_question_queue(questions, round_count)

    if round_seconds <= 0:
        raise GameEngineError("round_seconds must be greater than zero")

    return GameSessionState(
        session_id=session_id or uuid4().hex,
        players=tuple(players),
        question_queue=tuple(question_queue),
        round_seconds=round_seconds,
    )


def _build_players(player_names: list[str]) -> list[GamePlayer]:
    """Validate local player names and assign stable session-local ids."""

    if not 1 <= len(player_names) <= MAX_PLAYERS:
        raise GameEngineError("game session requires 1 to 6 players")

    players: list[GamePlayer] = []
    for index, raw_name in enumerate(player_names, start=1):
        name = raw_name.strip()
        if not name:
            raise GameEngineError("player name must not be empty")

        players.append(GamePlayer(id=f"player_{index}", name=name))

    return players


def _build_question_queue(
    questions: list[Question],
    round_count: int,
) -> list[Question]:
    """Validate and cut the provided questions to the session round count."""

    if round_count <= 0:
        raise GameEngineError("round_count must be greater than zero")

    if len(questions) < round_count:
        raise GameEngineError("not enough questions to create game session")

    return questions[:round_count]


def _build_answer_record(
    round_number: int,
    player: GamePlayer,
    judge_result: JudgeResult,
) -> GameAnswerRecord:
    """Convert judge output into session answer history."""

    return GameAnswerRecord(
        round_number=round_number,
        player_id=player.id,
        player_name=player.name,
        question_id=judge_result.question_id,
        submitted_answer=judge_result.submitted_answer,
        matched_answer=judge_result.matched_answer,
        is_correct=judge_result.is_correct,
        correct_answer=judge_result.correct_answer,
        explanation=judge_result.explanation,
        score_delta=judge_result.score_delta,
    )
