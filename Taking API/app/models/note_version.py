from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class NoteVersion(Base):
    __tablename__ = "note_versions"
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    version_number = Column(Integer)
    title = Column(String)
    markdown_content = Column(Text)
    tags_snapshot = Column(String) # Comma-separated tags
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    note = relationship("Note", back_populates="versions")
