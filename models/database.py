from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from config.config import DATABASE_URL

# پشتیبانی از PostgreSQL در Railway
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        # تبدیل postgres به postgresql برای سازگاری با SQLAlchemy
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine('sqlite:///bot.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(bind=engine)  # اضافه کردن SessionLocal

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    screenshot1 = Column(String)  # file_id of the first screenshot
    screenshot2 = Column(String)  # file_id of the second screenshot
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    verification_requested = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    verified_at = Column(DateTime, nullable=True)

class AdminMessage(Base):
    __tablename__ = 'admin_messages'
    id = Column(Integer, primary_key=True)
    message_type = Column(String)  # 'guide', 'welcome', etc.
    file_id = Column(String)
    caption = Column(String)
    updated_at = Column(DateTime, default=datetime.now)

# ایجاد جداول
try:
    Base.metadata.create_all(engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")