from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NoteBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, description="Short title")
    content: str = Field(min_length=1, max_length=200, description="Note content")


class Note(NoteBase, table=True):
    __tablename__ = "notes"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, min_length=1)


class NoteRead(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime