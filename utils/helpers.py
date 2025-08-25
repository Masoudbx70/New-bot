import sqlite3
from datetime import datetime, timedelta
import config.config as config
import threading

# ایجاد یک قفل برای thread-safe operations
lock = threading.Lock()

def get_cache_connection():
    """ایجاد اتصال به دیتابیس کش"""
    return sqlite3.connect('cache.db', check_same_thread=False)

def init_cache_db():
    """ایجاد جدول کش در صورت عدم وجود"""
    with lock:
        conn = get_cache_connection()
        cursor = conn.cursor()
        
        # ایجاد جدول کش
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # ایجاد ایندکس برای بهبود عملکرد
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expiry ON cache(expiry)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_key ON cache(key)')
        
        conn.commit()
        conn.close()

# مقداردهی اولیه دیتابیس کش
init_cache_db()

def _set_value(key, value, expire_seconds=3600):
    """ذخیره مقدار در کش با زمان انقضا"""
    with lock:
        conn = get_cache_connection()
        cursor = conn.cursor()
        
        expiry = (datetime.now() + timedelta(seconds=expire_seconds)) if expire_seconds else None
        
        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, expiry) VALUES (?, ?, ?)",
            (key, str(value), expiry)
        )
        
        conn.commit()
        conn.close()

def _get_value(key):
    """دریافت مقدار از کش با بررسی انقضا"""
    with lock:
        conn = get_cache_connection()
        cursor = conn.cursor()
        
        # حذف مقادیر منقضی شده
        cursor.execute("DELETE FROM cache WHERE expiry IS NOT NULL AND expiry < ?", 
                      (datetime.now(),))
        
        # دریافت مقدار
        cursor.execute("SELECT value FROM cache WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return result[0] if result else None

def _delete_value(key):
    """حذف مقدار از کش"""
    with lock:
        conn = get_cache_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        
        conn.commit()
        conn.close()

def _increment_value(key):
    """افزایش مقدار عددی"""
    with lock:
        current_value = int(_get_value(key) or 0)
        new_value = current_value + 1
        _set_value(key, new_value, 86400)  # انقضا پس از 24 ساعت
        return new_value

# توابع اصلی
def get_user_state(user_id):
    state = _get_value(f"user_state:{user_id}")
    return int(state) if state else None

def set_user_state(user_id, state):
    _set_value(f"user_state:{user_id}", state, 3600)  # انقضا پس از 1 ساعت

def delete_user_state(user_id):
    _delete_value(f"user_state:{user_id}")

def increment_message_count(user_id):
    return _increment_value(f"message_count:{user_id}")

def get_message_count(user_id):
    count = _get_value(f"message_count:{user_id}")
    return int(count) if count else 0

def reset_message_count(user_id):
    _delete_value(f"message_count:{user_id}")

def add_warning(user_id):
    warnings = _increment_value(f"warnings:{user_id}")
    return warnings

def get_warnings(user_id):
    warnings = _get_value(f"warnings:{user_id}")
    return int(warnings) if warnings else 0

def reset_warnings(user_id):
    _delete_value(f"warnings:{user_id}")

def cleanup_expired_cache():
    """پاک‌سازی مقادیر منقضی شده"""
    with lock:
        conn = get_cache_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cache WHERE expiry IS NOT NULL AND expiry < ?", 
                      (datetime.now(),))
        
        conn.commit()
        conn.close()