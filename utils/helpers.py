import re
from datetime import datetime
from telegram import Update
from models.database import Session, User

def is_user_verified(user_id: int) -> bool:
    """بررسی آیا کاربر احراز هویت شده است یا نه"""
    db_session = Session()
    user = db_session.query(User).filter(User.user_id == user_id).first()
    db_session.close()
    
    return user and user.is_verified

def validate_phone_number(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن"""
    pattern = r'^(\+98|0)?9\d{9}$'
    return re.match(pattern, phone) is not None

def validate_name(name: str) -> bool:
    """اعتبارسنجی نام و نام خانوادگی"""
    if not name or len(name.strip()) < 3:
        return False
    return True

def get_user_by_id(user_id: int):
    """دریافت اطلاعات کاربر بر اساس آیدی"""
    db_session = Session()
    user = db_session.query(User).filter(User.user_id == user_id).first()
    db_session.close()
    return user

def format_user_info(user: User) -> str:
    """قالب‌بندی اطلاعات کاربر برای نمایش"""
    return (
        f"👤 نام: {user.first_name} {user.last_name or ''}\n"
        f"📞 تلفن: {user.phone_number or 'ثبت نشده'}\n"
        f"🆔 آیدی: @{user.username or 'ندارد'}\n"
        f"✅ وضعیت: {'تأیید شده' if user.is_verified else 'در انتظار تأیید'}\n"
        f"📅 تاریخ ثبت: {user.created_at.strftime('%Y-%m-%d %H:%M')}"
    )