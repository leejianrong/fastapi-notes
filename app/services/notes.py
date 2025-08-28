from datetime import datetime, timezone
from typing import Iterable, Optional

from sqlmodel import Session, select

from app.db.models import Note, NoteCreate, NoteUpdate

def create_note(session: Session, payload: NoteCreate) -> Note:
    note = Note(**payload.model_dump())
    session.add(note)
    session.flush() # populate note.id
    return note


def list_notes(
    session: Session, 
    *, 
    offset: int = 0, 
    limit: int = 50
) -> Iterable[Note]:
    stmt = select(Note).order_by(Note.id).offset(offset).limit(limit)
    return session.exec(stmt).all()


def get_note(session: Session, note_id: int) -> Optional[Note]:
    return session.get(Note, note_id)


def update_note(session: Session, note: Note, patch: NoteUpdate) -> Note:
    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(note, k, v)
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.flush()
    return note


def delete_note(session: Session, note: Note) -> None:
    session.delete(note)
    session.flush()