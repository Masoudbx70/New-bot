import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(','))) if os.getenv("ADMIN_IDS") else []
GROUP_ID = int(os.getenv("GROUP_ID", 0))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

# سایر تنظیمات
MAX_MESSAGES_BEFORE_VERIFICATION = int(os.getenv("MAX_MESSAGES_BEFORE_VERIFICATION", 3))
TEMPORARY_BAN_DURATION = int(os.getenv("TEMPORARY_BAN_DURATION", 3600))  # 1 ساعت به ثانیه

# بررسی تنظیمات ضروری
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required")
if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS is required")
if not GROUP_ID:
    raise ValueError("GROUP_ID is required")