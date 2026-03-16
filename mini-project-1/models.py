from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date
from enum import Enum

class MembershipType(str, Enum):
    basic = "Basic"
    premium = "Premium"
    vip = "VIP"

class WorkoutSession(BaseModel):
    session_id: int
    date: date
    workout_type: str
    duration_minutes: int = Field(gt=0)   # can't be 0 or negative
    calories_burned: Optional[int] = None

class Member(BaseModel):
    member_id: int
    full_name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=18)               # gym rule: must be adult
    email: EmailStr
    membership_type: MembershipType
    sessions: List[WorkoutSession] = Field(default_factory=list)
