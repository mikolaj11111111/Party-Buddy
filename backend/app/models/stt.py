from sqlmodel import SQLModel


class SttResponse(SQLModel):
    """Response body for speech-to-text transcription."""

    text: str
