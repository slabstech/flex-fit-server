from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
import crud, models, schemas
from database import SessionLocal, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GymFit Gamification API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock auth (replace with real JWT later)
def get_current_user_id() -> int:
    return 1  # In real app: decode JWT

@app.post("/workouts/", response_model=schemas.WorkoutResponse)
def log_workout(
    workout: schemas.WorkoutCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user_id = get_current_user_id()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Create workout
    db_workout = models.Workout(user_id=user_id, **workout.dict())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)

    # === GAMIFICATION LOGIC ===
    today = date.today()
    xp_earned = calculate_xp_for_workout(workout.duration_min, workout.calories)

    old_level = user.level
    user.xp += xp_earned
    user.total_workouts += 1
    user.level = calculate_level(user.xp)

    # Streak logic
    if user.last_checkin_date != today:
        if should_reset_streak(user.last_checkin_date, today):
            user.streak_count = 1
        else:
            user.streak_count += 1
        user.last_checkin_date = today
        user.xp += XP_FOR_DAILY_CHECKIN  # Bonus for daily login
        xp_earned += XP_FOR_DAILY_CHECKIN

    new_badges = crud.award_badge_if_earned(db, user)
    db.commit()

    level_up = user.level > old_level

    # Optional: send push notification
    # background_tasks.add_task(send_streak_reminder, user)

    return {
        **db_workout.__dict__,
        "gamification": schemas.CheckinResponse(
            streak_count=user.streak_count,
            xp_earned=xp_earned,
            level_up=level_up,
            new_level=user.level if level_up else None,
            new_badges=new_badges
        )
    }

@app.get("/profile/gamification", response_model=schemas.CheckinResponse)
def get_gamification_status(db: Session = Depends(get_db)):
    user_id = get_current_user_id()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return schemas.CheckinResponse(
        streak_count=user.streak_count,
        xp_earned=0,
        level_up=False,
        new_level=user.level
    )

@app.get("/leaderboard/", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.xp.desc()).limit(50).all()
    return [
        schemas.LeaderboardEntry(
            username=u.username,
            level=u.level,
            xp=u.xp,
            streak_count=u.streak_count
        ) for u in users
    ]