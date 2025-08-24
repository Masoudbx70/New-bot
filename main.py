import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.ext import filters

from config import BOT_TOKEN, ADMIN_IDS
from handlers.group_handlers import setup_group_handlers
from handlers.auth_handlers import setup_auth_handlers
from handlers.admin_handlers import setup_admin_handlers

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # ایجاد آپدیتور و دیسپچر
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    # تنظیم هندلرهای مختلف
    setup_group_handlers(dp)
    setup_auth_handlers(dp)
    setup_admin_handlers(dp)

    # هندلر خطا
    dp.add_error_handler(error)

    # شروع ربات
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('WEBHOOK'):
        # استفاده از وب‌هوک برای Railway
        port = int(os.environ.get('PORT', 8443))
        updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{os.environ.get('RAILWAY_STATIC_URL')}.railway.app/{BOT_TOKEN}"
        )
    else:
        # استفاده از پولینگ برای توسعه محلی
        updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()