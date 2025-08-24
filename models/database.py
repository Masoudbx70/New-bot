from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz

from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    chat_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    screenshot1_file_id = Column(String)
    screenshot2_file_id = Column(String)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Tehran')))
    verified_at = Column(DateTime, nullable=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

# ایجاد جداول
Base.metadata.create_all(engine)