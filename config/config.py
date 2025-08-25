import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
GROUP_ID = int(os.getenv('GROUP_ID', 0))
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
REDIS_URL = os.getenv('REDIS_URL', 'sqlite:///cache.db')  # تغییر به SQLite

# وضعیت‌های کاربر
AWAITING_NAME, AWAITING_PHONE, AWAITING_SCREENSHOT_1, AWAITING_SCREENSHOT_2 = range(4)