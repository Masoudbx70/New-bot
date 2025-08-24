import os

# توکن ربات
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# آیدی ادمین‌ها (لیستی از آیدی عددی کاربران)
ADMIN_IDS = [int(id) for id in os.environ.get('ADMIN_IDS', '').split(',') if id]

# تنظیمات دیتابیس
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')

# سایر تنظیمات
MAX_MESSAGES_BEFORE_VERIFICATION = 3
TEMPORARY_BAN_MINUTES = 60