import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
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

async def error(update, context):
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    # ایجاد Application به جای Updater (در نسخه 20.x)
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ذخیره آیدی ادمین‌ها در context برای دسترسی در هندلرها
    application.bot_data['admin_ids'] = ADMIN_IDS

    # تنظیم هندلرهای مختلف
    setup_group_handlers(application)
    setup_auth_handlers(application)
    setup_admin_handlers(application)

    # هندلر خطا
    application.add_error_handler(error)

    # شروع ربات
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('WEBHOOK'):
        # استفاده از وب‌هوک برای Railway
        port = int(os.environ.get('PORT', 8443))
        webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'your-app-name')}.railway.app/{BOT_TOKEN}"
        
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # استفاده از پولینگ برای توسعه محلی
        application.run_polling()

if __name__ == '__main__':
    main()