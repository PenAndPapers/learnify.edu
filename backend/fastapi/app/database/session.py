import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_database_url

# Create Base class for models
Base = declarative_base()

# Create engine
engine = create_engine(get_database_url())

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger(__name__)


def get_db():
  db = SessionLocal()
  try:
    logger.debug("Database connection established")
    yield db
  except Exception as e:
    logger.error(f"Database error occurred: {str(e)}")
    raise
  finally:
    logger.debug("Database connection closed")
    db.close()
