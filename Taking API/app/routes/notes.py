from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.note import Note, Tag
from app.models.note_version import NoteVersion
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteVersionResponse
from app.services.markdown_service import convert_to_html
from app.services.cache_service import cache_rendered_html, get_rendered_html, invalidate_cache
from app.tasks.ai_tasks import process_note_background
from app.services.grammar_service import check_grammar
from app.utils.text_extractor import extract_plain_text
from app.utils.file_validator import validate_markdown_file
import uuid

router = APIRouter(prefix="/notes", tags=["Notes"])

def get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    tags = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags

@router.post("", response_model=NoteResponse)
def create_note(note_in: NoteCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    note = Note(title=note_in.title, markdown_content=note_in.markdown_content)
    if note_in.tags:
        note.tags = get_or_create_tags(db, note_in.tags)
    
    db.add(note)
    db.commit()
    db.refresh(note)

    # Render and cache HTML
    html = convert_to_html(note.markdown_content)
    cache_rendered_html(note.id, html)

    # Background task
    background_tasks.add_task(process_note_background, note.id)
    
    return note

@router.get("/search", response_model=List[NoteResponse])
def search_notes(
    db: Session = Depends(get_db),
    keyword: Optional[str] = None,
    tag: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    query = db.query(Note)

    if keyword:
        query = query.filter(Note.title.ilike(f"%{keyword}%") | Note.markdown_content.ilike(f"%{keyword}%"))
    if tag:
        query = query.filter(Note.tags.any(Tag.name == tag))
    if date_from:
        query = query.filter(Note.created_at >= date_from)
    if date_to:
        query = query.filter(Note.created_at <= date_to)

    return query.all()

@router.get("", response_model=List[NoteResponse])
def list_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()

@router.get("/{id}", response_model=NoteResponse)
def get_note(id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{id}", response_model=NoteResponse)
def update_note(id: int, note_in: NoteUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Save previous version
    last_version = db.query(NoteVersion).filter(NoteVersion.note_id == id).order_by(NoteVersion.version_number.desc()).first()
    version_number = last_version.version_number + 1 if last_version else 1

    version = NoteVersion(
        note_id=id,
        version_number=version_number,
        title=note.title,
        markdown_content=note.markdown_content,
        tags_snapshot=",".join([t.name for t in note.tags])
    )
    db.add(version)

    # Update note
    note.title = note_in.title
    note.markdown_content = note_in.markdown_content
    if note_in.tags is not None:
        note.tags = get_or_create_tags(db, note_in.tags)

    db.commit()
    db.refresh(note)

    # Invalidate and update cache
    invalidate_cache(note.id)
    html = convert_to_html(note.markdown_content)
    cache_rendered_html(note.id, html)

    background_tasks.add_task(process_note_background, note.id)

    return note

@router.delete("/{id}")
def delete_note(id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    invalidate_cache(id)
    return {"message": "Note deleted"}

@router.get("/{id}/rendered")
def get_note_rendered(id: int, db: Session = Depends(get_db)):
    html = get_rendered_html(id)
    if not html:
        note = db.query(Note).filter(Note.id == id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        html = convert_to_html(note.markdown_content)
        cache_rendered_html(id, html)
    return {"html": html}

@router.get("/{id}/versions", response_model=List[NoteVersionResponse])
def get_note_versions(id: int, db: Session = Depends(get_db)):
    versions = db.query(NoteVersion).filter(NoteVersion.note_id == id).order_by(NoteVersion.version_number.desc()).all()
    return versions

@router.get("/{id}/versions/{version_number}", response_model=NoteVersionResponse)
def get_note_version(id: int, version_number: int, db: Session = Depends(get_db)):
    version = db.query(NoteVersion).filter(NoteVersion.note_id == id, NoteVersion.version_number == version_number).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.post("/{id}/grammar-check")
def check_note_grammar(id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    plain_text = extract_plain_text(note.markdown_content)
    issues = check_grammar(plain_text)
    return {"issues": issues}

@router.post("/upload", response_model=NoteResponse)
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    markdown_content = await validate_markdown_file(file)
    title = file.filename.rsplit('.', 1)[0]

    note = Note(title=title, markdown_content=markdown_content)
    db.add(note)
    db.commit()
    db.refresh(note)

    html = convert_to_html(note.markdown_content)
    cache_rendered_html(note.id, html)
    background_tasks.add_task(process_note_background, note.id)

    return note
