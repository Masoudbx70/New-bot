import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.config import BOT_TOKEN, ADMIN_IDS
from handlers import group_handlers, auth_handlers, admin_handlers, support_handlers

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # ایجاد برنامه
    application = Application.builder().token(BOT_TOKEN).build()
    
    # افزودن هندلرهای گروه
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_handlers.welcome_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_handlers.goodbye_member))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_handlers.handle_group_message))
    
    # افزودن هندلرهای احراز هویت
    application.add_handler(CommandHandler("start", auth_handlers.start))
    application.add_handler(CommandHandler("verify", auth_handlers.start_verification))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, auth_handlers.handle_verification))
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, auth_handlers.handle_screenshot))
    
    # افزودن هندلرهای مدیریت
    application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    application.add_handler(CommandHandler("members_list", admin_handlers.members_list))
    
    # افزودن هندلرهای پشتیبانی
    application.add_handler(CommandHandler("help", support_handlers.help_command))
    application.add_handler(CommandHandler("support", support_handlers.support))
    
    # شروع ربات
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # اجرا در Railway
        port = int(os.environ.get("PORT", 8443))
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"https://{os.environ.get('RAILWAY_STATIC_URL')}.railway.app/{BOT_TOKEN}"
        )
    else:
        # اجرا به صورت محلی
        application.run_polling()

if __name__ == "__main__":
    main()