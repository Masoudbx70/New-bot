import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.ext import filters

from config import BOT_TOKEN, ADMIN_IDS

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error(update, context):
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    # ایجاد Application به جای Updater (در نسخه 20.x)
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ذخیره آیدی ادمین‌ها در context برای دسترسی در هندلرها
    application.bot_data['admin_ids'] = ADMIN_IDS

    # ایمپورت و تنظیم هندلرها
    from handlers.group_handlers import setup_group_handlers
    from handlers.auth_handlers import setup_auth_handlers
    from handlers.admin_handlers import setup_admin_handlers
    
    setup_group_handlers(application)
    setup_auth_handlers(application)
    setup_admin_handlers(application)

    # هندلر خطا
    application.add_error_handler(error)

    # استفاده از پولینگ (ساده‌تر و بدون نیاز به تنظیمات اضافه)
    print("🤖 ربات در حال راه‌اندازی با روش Polling...")
    application.run_polling()

if __name__ == '__main__':
    main()