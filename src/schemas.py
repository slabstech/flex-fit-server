from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class WorkoutCreate(BaseModel):
    workout_type: str
    duration_min: int
    calories: Optional[int] = None

class WorkoutResponse(WorkoutCreate):
    id: int
    created_at: datetime

class CheckinResponse(BaseModel):
    streak_count: int
    xp_earned: int
    level_up: bool = False
    new_level: Optional[int] = None
    new_badges: List[str] = []

class LeaderboardEntry(BaseModel):
    username: str
    level: int
    xp: int
    streak_count: int

class BadgeResponse(BaseModel):
    name: str
    description: str
    icon_url: str
    earned_at: datetime