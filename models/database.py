from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

# خواندن DATABASE_URL از محیط
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# تعریف یک alias برای Session مثل قبل
Session = SessionLocal

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_requested = Column(Boolean, default=False)
    screenshot1 = Column(String, nullable=True)
    screenshot2 = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    verified_at = Column(DateTime, nullable=True)

class AdminMessage(Base):
    __tablename__ = "admin_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# ساخت جداول در صورت وجود نداشتن
def init_db():
    Base.metadata.create_all(bind=engine)