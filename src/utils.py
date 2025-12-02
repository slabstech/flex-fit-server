from datetime import date, timedelta
from typing import List

XP_PER_WORKOUT = 50
XP_PER_MINUTE = 2
XP_FOR_DAILY_CHECKIN = 20

def calculate_xp_for_workout(duration_min: int, calories: int = None) -> int:
    return XP_PER_WORKOUT + (duration_min * XP_PER_MINUTE)

def xp_to_next_level(current_level: int) -> int:
    return 100 * current_level * current_level  # Quadratic: level 1→100, 2→400, 3→900...

def calculate_level(total_xp: int) -> int:
    level = 1
    while total_xp >= xp_to_next_level(level):
        total_xp -= xp_to_next_level(level)
        level += 1
    return level

def should_reset_streak(last_checkin: date | None, today: date) -> bool:
    if not last_checkin:
        return True
    return (today - last_checkin) > timedelta(days=1)