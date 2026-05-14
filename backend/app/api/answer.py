from fastapi import APIRouter, HTTPException, status

from backend.app.core.answer_service import QuestionNotFoundError, answer_question
from backend.app.core.question_loader import QuestionLoaderError
from backend.app.models.answer import AnswerRequest, AnswerResponse

router = APIRouter(prefix="/api/answer", tags=["answer"])


@router.post("", response_model=AnswerResponse)
def submit_answer(answer_request: AnswerRequest) -> AnswerResponse:
    """Accept one answer submission and return deterministic judge result."""

    try:
        return answer_question(answer_request)
    except QuestionNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except QuestionLoaderError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
