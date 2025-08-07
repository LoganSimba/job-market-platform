from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_text = Column(String(100), nullable=True)  # Original salary string
    skills = Column(Text, nullable=True)  # Comma-separated skills
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    remote = Column(String(20), nullable=True)  # "Remote", "Hybrid", "On-site"
    date_posted = Column(DateTime, default=func.now())
    date_scraped = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', location='{self.location}')>"