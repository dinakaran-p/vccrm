from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use localhost since we can see PostgreSQL running on port 5432
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vccrm:vccrm@localhost:5432/vccrm")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
