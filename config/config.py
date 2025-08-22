import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(',')))
GROUP_ID = int(os.getenv("GROUP_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

# سایر تنظیمات
MAX_MESSAGES_BEFORE_VERIFICATION = 3
TEMPORARY_BAN_DURATION = 3600  # 1 ساعت به ثانیه