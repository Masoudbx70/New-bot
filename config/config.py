# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
GROUP_ID = int(os.getenv("GROUP_ID", "0")) if os.getenv("GROUP_ID") else None
DATABASE_URL = os.getenv("DATABASE_URL", "")

MAX_MESSAGES_BEFORE_VERIFICATION = int(os.getenv("MAX_MESSAGES_BEFORE_VERIFICATION", 3))
TEMPORARY_BAN_DURATION = int(os.getenv("TEMPORARY_BAN_DURATION", 3600))