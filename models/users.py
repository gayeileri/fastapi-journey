from typing import List, Optional
from beanie import Document, Link
from pydantic import BaseModel, EmailStr

from models.events import Event


# user model
class User(Document):
    email: EmailStr
    password: str
    events: Optional[List[Link[Event]]] = None  # list of events the user has

    class Settings:
        name = "users"


# only used when signing in
class UserSignIn(BaseModel):
    email: EmailStr
    password: str
