from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from config.config import DATABASE_URL

# پشتیبانی از PostgreSQL در Railway
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    engine = create_engine(DATABASE_URL)
elif DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # تبدیل postgres به postgresql برای سازگاری با SQLAlchemy
    engine = create_engine(DATABASE_URL.replace("postgres://", "postgresql://"))
else:
    engine = create_engine('sqlite:///bot.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    # ... (بقیه کد بدون تغییر)

class AdminMessage(Base):
    __tablename__ = 'admin_messages'
    # ... (بقیه کد بدون تغییر)

# ایجاد جداول
try:
    Base.metadata.create_all(engine)
except Exception as e:
    print(f"Error creating database tables: {e}")