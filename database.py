from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
import os

# Database configuration
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./jobs.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    from models.job import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    create_tables()