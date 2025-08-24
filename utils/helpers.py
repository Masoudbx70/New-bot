# utils/helpers.py
import re
from datetime import datetime
from typing import Optional
from models.database import SessionLocal, User

def is_user_verified(user_id: int) -> bool:
    """بررسی آیا کاربر احراز هویت شده است یا نه"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        return bool(user and user.is_verified)
    finally:
        db.close()

def validate_phone_number(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن (ایران)"""
    if not phone:
        return False
    # پذیرش فرمت +989... یا 09...
    pattern = r'^(\+98|0)?9\d{9}$'
    return re.match(pattern, phone) is not None

def validate_name(name: str) -> bool:
    """اعتبارسنجی نام و نام خانوادگی"""
    if not name or len(name.strip()) < 3:
        return False
    return True

def get_user_by_id(user_id: int) -> Optional[User]:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    finally:
        db.close()

def format_user_info(user: User) -> str:
    """قالب‌بندی اطلاعات کاربر برای نمایش"""
    created_at = user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'ثبت نشده'
    return (
        f"👤 نام: {user.first_name or ''} {user.last_name or ''}\n"
        f"📞 تلفن: {user.phone_number or 'ثبت نشده'}\n"
        f"🆔 آیدی: @{user.username or 'ندارد'}\n"
        f"✅ وضعیت: {'تأیید شده' if user.is_verified else 'در انتظار تأیید'}\n"
        f"📅 تاریخ ثبت: {created_at}"
    )