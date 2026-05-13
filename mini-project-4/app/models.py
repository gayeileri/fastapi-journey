# Pydantic models for the API
from pydantic import BaseModel
from typing import List, Optional


class PollCreate(BaseModel):
    question: str
    options: List[str]
    

class Vote(BaseModel):
    option_id: int


class PollResponse(BaseModel):
    id: int
    question: str
    options: List[dict]  # [{"id": 0, "text": "option1", "votes": 5}, ...]
    
    class Config:
        from_attributes = True
