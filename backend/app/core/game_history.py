from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session as DbSession
from sqlmodel import select

from backend.app.core.game_engine import GameSessionState
from backend.app.db import engine
from backend.app.models.history import GameHistoryScore, GameHistorySession
from backend.app.models.profile import Profile
from backend.app.models.score import Score
from backend.app.models.session import Session as StoredSession
from backend.app.models.session import SessionMode, SessionStatus

GLOBAL_PROFILE_ID = "global"


class GameHistoryError(ValueError):
    """Raised when finished game history cannot be persisted or listed."""

    pass


class GameHistoryRecorder:
    """Persists finished in-memory game sessions to SQLite."""

    def __init__(
        self,
        db_session_factory: Callable[[], AbstractContextManager[DbSession]]
        | None = None,
    ) -> None:
        """Store a DB session factory for production or tests."""

        self._db_session_factory = db_session_factory or (lambda: DbSession(engine))

    def save_finished_session(
        self,
        game_session: GameSessionState,
        *,
        started_at: datetime,
        finished_at: datetime,
    ) -> GameHistorySession:
        """Persist a finished game session using a short-lived DB session."""

        with self._db_session_factory() as db_session:
            return save_finished_game_session(
                db_session,
                game_session,
                started_at=started_at,
                finished_at=finished_at,
            )


def save_finished_game_session(
    db_session: DbSession,
    game_session: GameSessionState,
    *,
    started_at: datetime,
    finished_at: datetime,
) -> GameHistorySession:
    """Save a completed in-memory session and return its public summary."""

    if game_session.status != "finished":
        raise GameHistoryError("only finished game sessions can be saved")

    existing_session = db_session.get(StoredSession, game_session.session_id)
    if existing_session is not None:
        return _build_history_session(
            existing_session,
            _list_scores_for_session(db_session, existing_session.id),
        )

    _ensure_global_profile(db_session)
    stored_session = StoredSession(
        id=game_session.session_id,
        profile_id=GLOBAL_PROFILE_ID,
        mode=_session_mode(game_session),
        status=SessionStatus.finished,
        total_rounds=game_session.round_count,
        round_seconds=game_session.round_seconds,
        current_round=game_session.round_count,
        created_at=started_at,
        finished_at=finished_at,
    )
    score_rows = _build_score_rows(game_session)

    try:
        db_session.add(stored_session)
        db_session.add_all(score_rows)
        db_session.commit()
    except SQLAlchemyError as error:
        db_session.rollback()
        raise GameHistoryError("could not save game history") from error

    return _build_history_session(stored_session, score_rows)


def list_finished_game_sessions(
    db_session: DbSession,
    *,
    limit: int = 20,
) -> list[GameHistorySession]:
    """Return finished sessions with their stored player scores."""

    statement = (
        select(StoredSession)
        .where(StoredSession.status == SessionStatus.finished)
        .order_by(StoredSession.finished_at.desc(), StoredSession.created_at.desc())
        .limit(limit)
    )
    sessions = db_session.exec(statement).all()

    return [
        _build_history_session(
            stored_session,
            _list_scores_for_session(db_session, stored_session.id),
        )
        for stored_session in sessions
    ]


def _ensure_global_profile(db_session: DbSession) -> None:
    """Create the MVP global profile if it does not exist yet."""

    if db_session.get(Profile, GLOBAL_PROFILE_ID) is None:
        db_session.add(Profile(id=GLOBAL_PROFILE_ID, display_name="Player"))


def _session_mode(game_session: GameSessionState) -> SessionMode:
    """Infer solo or hotseat mode from the number of local players."""

    return SessionMode.solo if len(game_session.players) == 1 else SessionMode.hotseat


def _build_score_rows(game_session: GameSessionState) -> list[Score]:
    """Build stored score rows from answer history and final scoreboard."""

    player_order = {
        player.id: index for index, player in enumerate(game_session.players)
    }
    answers_by_player = {
        player.id: [
            answer
            for answer in game_session.answer_history
            if answer.player_id == player.id
        ]
        for player in game_session.players
    }

    return [
        Score(
            session_id=game_session.session_id,
            player_id=player.id,
            player_name=player.name,
            player_order=player_order[player.id],
            score=game_session.scores[player.id],
            correct_answers=sum(
                1 for answer in answers_by_player[player.id] if answer.is_correct
            ),
            answered_questions=len(answers_by_player[player.id]),
        )
        for player in game_session.players
    ]


def _list_scores_for_session(
    db_session: DbSession,
    session_id: str,
) -> list[Score]:
    """Load score rows for one session in ranking order."""

    statement = (
        select(Score)
        .where(Score.session_id == session_id)
        .order_by(Score.score.desc(), Score.player_order.asc())
    )
    return list(db_session.exec(statement).all())


def _build_history_session(
    stored_session: StoredSession,
    scores: list[Score],
) -> GameHistorySession:
    """Convert stored SQLModel rows into the public history schema."""

    top_score = scores[0].score if scores else 0
    winners = [score.player_name for score in scores if score.score == top_score]
    return GameHistorySession(
        id=stored_session.id,
        mode=stored_session.mode,
        total_rounds=stored_session.total_rounds,
        round_seconds=stored_session.round_seconds,
        created_at=stored_session.created_at,
        finished_at=stored_session.finished_at,
        top_score=top_score,
        winners=winners,
        players=[
            GameHistoryScore(
                player_id=score.player_id,
                player_name=score.player_name,
                player_order=score.player_order,
                score=score.score,
                correct_answers=score.correct_answers,
                answered_questions=score.answered_questions,
            )
            for score in scores
        ],
    )
