from sqlalchemy.orm import Session
from datetime import date
import models
from utils import *

def award_badge_if_earned(db: Session, user: models.User):
    today = date.today()
    earned_badges = []

    badges = db.query(models.Badge).all()
    existing = {ub.badge_id for ub in user.user_badges}

    for badge in badges:
        if badge.id in existing:
            continue

        earned = False
        if badge.criteria_type == "streak" and user.streak_count >= badge.criteria_value:
            earned = True
        elif badge.criteria_type == "total_workouts" and user.total_workouts >= badge.criteria_value:
            earned = True

        if earned:
            user_badge = models.UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            earned_badges.append(badge.name)

    return earned_badges