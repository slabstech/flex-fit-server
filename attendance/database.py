# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure the database file is in the writable /app directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# This is the correct way — connect_args appears only once
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite in FastAPI
    # Optional: make file writable by all (only needed if permissions are strict)
    # Remove this line if you use the volume method below
    # connect_args={"check_same_thread": False, "timeout": 30},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()