import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_database_url

# Create Base class for models
Base = declarative_base()

# Create engine
engine = create_engine(
  get_database_url(),
  pool_size=20,
  max_overflow=50,
  pool_timeout=30,
  pool_recycle=1800,
  pool_pre_ping=True,
  pool_use_lifo=True,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger(__name__)


def get_db():
  db = SessionLocal()
  try:
    logger.debug("Database connection is established. Starting transaction.")
    yield db

    # If the request finishes and reaches this line without raising an exception,
    # we commit the entire transaction atomically here.
    db.commit()
  except Exception as e:
    # If ANY exception or HTTPException was raised anywhere in the route,
    # service, or repository, we catch it here and roll back completely.
    db.rollback()
    logger.error(f"Database error has occurred, transaction rolled back: {str(e)}")
    raise
  finally:
    logger.debug("Database connection is closed.")
    db.close()


# Package-level dependency for FastAPI dependency injection
DatabaseDep = Annotated[Session, Depends(get_db)]
