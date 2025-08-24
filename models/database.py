# models/database.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # فایل sqlite محلی پیش‌فرض
    engine = create_engine('sqlite:///bot.db', echo=False, connect_args={"check_same_thread": False})

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    screenshot1 = Column(String, nullable=True)
    screenshot2 = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    verification_requested = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

class AdminMessage(Base):
    __tablename__ = 'admin_messages'

    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String)  # 'guide', 'welcome', etc.
    file_id = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

# ایجاد جداول (ایمن برای بار اول)
def init_db():
    Base.metadata.create_all(bind=engine)

# اجرای اولیه ساخت جداول هنگام ایمپورت main
init_db()