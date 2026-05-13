from sqlmodel import SQLModel


class SttResponse(SQLModel):
    text: str
