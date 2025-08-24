import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',')] if ADMIN_IDS_STR else []
GROUP_ID_STR = os.getenv("GROUP_ID", "")
GROUP_ID = int(GROUP_ID_STR) if GROUP_ID_STR.isdigit() else None
DATABASE_URL = os.getenv("DATABASE_URL")

# سایر تنظیمات
MAX_MESSAGES_BEFORE_VERIFICATION = 3
TEMPORARY_BAN_DURATION = 3600  # 1 ساعت به ثانیه

# بررسی تنظیمات ضروری
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")

if not ADMIN_IDS:
    print("Warning: ADMIN_IDS is empty. Admin features will not work.")

if not GROUP_ID:
    print("Warning: GROUP_ID is not set. Group features will not work.")