# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional

# === User Schemas ===
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    level: int = 1
    xp: int = 0
    streak_count: int = 0
    total_workouts: int = 0

    class Config:
        from_attributes = True


# === Existing Workout & Gamification Schemas ===
class WorkoutCreate(BaseModel):
    workout_type: str
    duration_min: int
    calories: Optional[int] = None

class WorkoutResponse(WorkoutCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True