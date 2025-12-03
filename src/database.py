from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# For local development without Docker
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/fitness"  # Docker default
)

# When running outside Docker (e.g. locally with Docker running)
# fallback to localhost if needed:
if os.getenv("USE_LOCALHOST_DB"):
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/fitness"

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fitness"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()