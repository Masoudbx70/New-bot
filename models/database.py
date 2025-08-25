from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz
import config.config as config

# تنظیم منطقه زمانی ایران
tehran_tz = pytz.timezone('Asia/Tehran')

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_tehran_time():
    return datetime.now(tehran_tz)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    screenshot_1 = Column(String, nullable=True)
    screenshot_2 = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    join_date = Column(DateTime, default=get_tehran_time)
    message_count = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    is_temporarily_banned = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=get_tehran_time, onupdate=get_tehran_time)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()