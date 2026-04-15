from typing import List, Optional
from beanie import Document
from pydantic import BaseModel


# Event model - this is what we store in the database
class Event(Document):
    title: str
    image: str
    description: str
    tags: List[str]
    location: str

    class Settings:
        name = "events"


# This model is used for update operations
# all fields are optional because the user might only want to change one thing
class EventUpdate(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
