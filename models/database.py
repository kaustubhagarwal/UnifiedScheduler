from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import enum
from datetime import datetime, time

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    PARTIAL = "Partial"
    COMPLETED = "Completed"

class TaskType(enum.Enum):
    REGULAR = "Regular Task"
    DAILY = "Daily Activity"

class RecurrencePattern(enum.Enum):
    NONE = "None"
    DAILY = "Daily"
    WEEKDAYS = "Weekdays"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.NOT_STARTED)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # New fields
    task_type = Column(Enum(TaskType), nullable=False, default=TaskType.REGULAR)
    is_fixed_time = Column(Boolean, default=False)
    fixed_time = Column(Time, nullable=True)
    flexible_start_time = Column(Time, nullable=True)
    flexible_end_time = Column(Time, nullable=True)
    recurrence_pattern = Column(Enum(RecurrencePattern), nullable=False, default=RecurrencePattern.NONE)
    estimated_duration = Column(Integer, nullable=True)  # Duration in minutes

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()