import logging
from datetime import datetime, timezone
from typing import Iterable, Optional

from sqlmodel import Session, select

from app.db.models import Note, NoteCreate, NoteUpdate

log = logging.getLogger("notes")

def create_note(session: Session, payload: NoteCreate) -> Note:
    note = Note(**payload.model_dump())
    session.add(note)
    session.flush() # populate note.id

    log.info(
        "note_created",
        extra={
            "note_id": note.id,
            "title": note.title,
            "service": "notes-api",
        },
    )
    return note


def list_notes(
    session: Session, 
    *, 
    offset: int = 0, 
    limit: int = 50
) -> Iterable[Note]:
    stmt = select(Note).order_by(Note.id).offset(offset).limit(limit)
    notes = session.exec(stmt).all()
    log.debug(
        "notes_listed",
        extra={
            "count": len(notes),
            "offset": offset,
            "limit": limit,
            "service": "notes-api"
        },
    )
    return notes


def get_note(session: Session, note_id: int) -> Optional[Note]:
    note = session.get(Note, note_id)
    if note:
        log.info(
            "note_read",
            extra={
                "note_id": note_id,
                "service": "notes-api",
            },
        )
    else:
        log.warning(
            "note_read_not_found",
            extra={
                "note_id": note_id,
                "service": "notes-api",
            },
        )
    return note

def update_note(session: Session, note: Note, patch: NoteUpdate) -> Note:
    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(note, k, v)
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.flush()

    log.info(
        "note_updated",
        extra={
            "note_id": note.id,
            "changed_fields": list(data.keys()),
            "service": "notes-api",
        },
    )
    return note


def delete_note(session: Session, note: Note) -> None:
    nid = note.id
    session.delete(note)
    session.flush()
    log.info(
        "note_deleted",
        extra={
            "note_id": nid,
            "service": "notes-api",
        },
    )