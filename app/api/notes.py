import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.db.deps import get_session
from app.db.models import Note, NoteCreate, NoteUpdate, NoteRead
from app.services import notes as notes_service

edge_log = logging.getLogger("notes.edge")
router = APIRouter(prefix="/notes", tags=["notes"])

@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
)
def create_note(payload: NoteCreate, session: Session = Depends(get_session)):
    note = notes_service.create_note(session, payload)
    return note


@router.get(
    "",
    response_model=List[NoteRead],
    summary="List notes (paginated)",
)
def list_notes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    return notes_service.list_notes(session, offset=offset, limit=limit)


@router.get(
    "/{note_id}",
    response_model=NoteRead,
    summary="Get a node by id",
)
def get_note(
    note_id: int = Path(..., ge=1),
    session: Session = Depends(get_session),
):
    note = notes_service.get_note(session, note_id)
    if not note:
        edge_log.warning(
            "http_404_note", 
            extra={
                "note_id": note_id,
                "route": "GET /notes/{note_id}",
                "service": "notes-api"
            }
        )
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch(
    "/{note_id}",
    response_model=NoteRead,
    summary="Update a note",
)
def update_note(
    note_id: int = Path(..., ge=1),
    patch: NoteUpdate = ...,
    session: Session = Depends(get_session),
):
    note = notes_service.get_note(session, note_id)
    if not note:
        edge_log.warning(
            "http_404_note", 
            extra={
                "note_id": note_id,
                "route": "PATCH /notes/{note_id}",
                "service": "notes-api"
            }
        )
        raise HTTPException(status_code=404, detail="Note not found")
    updated = notes_service.update_note(session, note, patch)
    return updated    


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
)
def delete_note(
    note_id: int = Path(..., ge=1),
    session: Session = Depends(get_session),
):
    note = notes_service.get_note(session, note_id)
    if not note:
        edge_log.warning(
            "http_404_note", 
            extra={
                "note_id": note_id,
                "route": "DELETE /notes/{note_id}",
                "service": "notes-api"
            }
        )
        raise HTTPException(status_code=404, detail="Note not found")
    notes_service.delete_note(session, note)
    return None