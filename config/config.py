import os

# توکن ربات - الزامی
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# آیدی ادمین‌ها (لیستی از آیدی عددی کاربران) - الزامی
admin_ids_str = os.environ.get('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()] if admin_ids_str else []

# آیدی گروه (اختیاری)
GROUP_ID = os.environ.get('GROUP_ID', None)

# تنظیمات دیتابیس
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')

# سایر تنظیمات
MAX_MESSAGES_BEFORE_VERIFICATION = int(os.environ.get('MAX_MESSAGES_BEFORE_VERIFICATION', '3'))
TEMPORARY_BAN_MINUTES = int(os.environ.get('TEMPORARY_BAN_MINUTES', '60'))

# بررسی تنظیمات ضروری
if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    raise ValueError("لطفاً توکن ربات را در متغیر محیطی BOT_TOKEN تنظیم کنید")

if not ADMIN_IDS:
    print("⚠️  هشدار: هیچ آیدی ادمینی تنظیم نشده است. لطفاً ADMIN_IDS را تنظیم کنید")