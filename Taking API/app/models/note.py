from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

note_tag_association = Table(
    'note_tag', Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    markdown_content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    summary = Column(Text, nullable=True)
    suggested_tags = Column(String, nullable=True) # Stored as comma-separated
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    tags = relationship("Tag", secondary=note_tag_association, backref="notes")
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan")
    user = relationship("User", back_populates="notes")

