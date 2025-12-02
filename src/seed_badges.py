# seed_badges.py
from database import SessionLocal
from models import Badge

badges = [
    {"name": "First Workout", "criteria_type": "total_workouts", "criteria_value": 1},
    {"name": "Week Warrior", "criteria_type": "streak", "criteria_value": 7},
    {"name": "Century Club", "criteria_type": "total_workouts", "criteria_value": 100},
]

db = SessionLocal()
for b in badges:
    db.add(Badge(**b, description=f"Earned {b['name']}", icon_url="https://example.com/badge.png"))
db.commit()