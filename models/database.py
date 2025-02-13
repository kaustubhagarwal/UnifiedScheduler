from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Boolean, Time, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import enum
from datetime import datetime, time

# Get database URL from environment variable
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'local_database.db')}"

engine = create_engine(DATABASE_URL, echo=True)
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

class AccountType(enum.Enum):
    BANK = "Bank Account"
    CREDIT = "Credit Card"
    CASH = "Cash"
    INVESTMENT = "Investment"
    OTHER = "Other"

class TransactionType(enum.Enum):
    INCOME = "Income"
    EXPENSE = "Expense"
    TRANSFER = "Transfer"

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

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="USD")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    is_active = Column(Boolean, default=True)

    # Relationships
    transactions = relationship("Transaction", back_populates="account")

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=False)  # For visualization purposes
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationships
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey('accounts.id'), nullable=False)
    category_id = Column(String, ForeignKey('categories.id'), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()