# main.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import crud, models, schemas
from database import SessionLocal, engine, Base
from typing import List
from utils import (
    calculate_xp_for_workout, xp_to_next_level, calculate_level,
    should_reset_streak, XP_PER_WORKOUT, XP_FOR_DAILY_CHECKIN
)
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

# === Security Setup ===
SECRET_KEY = "your-super-secret-jwt-key-change-in-production!!!"  # Use env var!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GymFit Gamification API")


# === Dependency ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Auth Utilities ===
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# === Routes ===

@app.post("/register/", response_model=schemas.UserPublic, status_code=201)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(400, "Username already taken")

    hashed_password = get_password_hash(user_in.password)
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/workouts/", response_model=schemas.WorkoutResponse)
def log_workout(
    workout: schemas.WorkoutCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Create workout
    db_workout = models.Workout(user_id=current_user.id, **workout.dict())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)

    # === GAMIFICATION LOGIC ===
    today = date.today()
    xp_earned = calculate_xp_for_workout(workout.duration_min, workout.calories)

    old_level = current_user.level
    current_user.xp += xp_earned
    current_user.total_workouts += 1
    current_user.level = calculate_level(current_user.xp)

    # Daily check-in & streak
    if current_user.last_checkin_date != today:
        if should_reset_streak(current_user.last_checkin_date, today):
            current_user.streak_count = 1
        else:
            current_user.streak_count += 1
        current_user.last_checkin_date = today
        current_user.xp += XP_FOR_DAILY_CHECKIN
        xp_earned += XP_FOR_DAILY_CHECKIN

    new_badges = crud.award_badge_if_earned(db, current_user)
    db.commit()

    level_up = current_user.level > old_level

    return {
        **db_workout.__dict__,
        "gamification": schemas.CheckinResponse(
            streak_count=current_user.streak_count,
            xp_earned=xp_earned,
            level_up=level_up,
            new_level=current_user.level if level_up else None,
            new_badges=new_badges
        )
    }


@app.get("/profile/gamification", response_model=schemas.CheckinResponse)
def get_gamification_status(current_user: models.User = Depends(get_current_user)):
    return schemas.CheckinResponse(
        streak_count=current_user.streak_count,
        xp_earned=0,
        level_up=False,
        new_level=current_user.level,
        new_badges=[]
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