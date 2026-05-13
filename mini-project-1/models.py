from pydantic import BaseModel
from typing import List, Optional


class WorkoutSession(BaseModel):
    session_id: int
    date: str
    workout_type: str
    duration_minutes: int
    calories_burned: Optional[int] = None


class Member(BaseModel):
    id: int
    name: str
    membership_type: str  # Basic, Premium ya da VIP olabilir
    sessions: List[WorkoutSession] = []
