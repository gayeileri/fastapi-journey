from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    title: str
    markdown_content: str
    tags: Optional[List[str]] = []

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteResponse(BaseModel):
    id: int
    title: str
    markdown_content: str
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None
    suggested_tags: Optional[str] = None
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

class NoteVersionResponse(BaseModel):
    id: int
    version_number: int
    title: str
    markdown_content: str
    tags_snapshot: str
    created_at: datetime

    class Config:
        from_attributes = True

class GrammarIssueResponse(BaseModel):
    issue: str
    context: str
    suggestions: List[str]
    offset: int
    length: int
