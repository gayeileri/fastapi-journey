from pydantic import BaseModel, constr
from typing import List, Optional
from datetime import datetime

# Tag names must be strictly alphanumeric (no spaces/hyphens/underscores/specials)
# Pydantic v2 uses `pattern` for regex validation
TagStr = constr(pattern=r'^[A-Za-z0-9]+$')


class TagBase(BaseModel):
    name: TagStr


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True


class NoteBase(BaseModel):
    # Title must not exceed 200 characters
    title: constr(max_length=200)
    markdown_content: str
    tags: Optional[List[TagStr]] = []


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
