import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config.config import BOT_TOKEN, ADMIN_IDS
from handlers import group_handlers, auth_handlers, admin_handlers, support_handlers

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    """تابع برای تنظیم webhook بعد از راه‌اندازی"""
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # تنظیم webhook در Railway
        webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL')}.railway.app/{BOT_TOKEN}"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")

def main():
    # ایجاد برنامه
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
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
    application.add_handler(CommandHandler("pending_requests", admin_handlers.pending_requests))
    application.add_handler(CallbackQueryHandler(admin_handlers.handle_admin_callback))
    
    # افزودن هندلرهای پشتیبانی
    application.add_handler(CommandHandler("help", support_handlers.help_command))
    application.add_handler(CommandHandler("support", support_handlers.support))
    application.add_handler(MessageHandler(filters.CONTACT & filters.ChatType.PRIVATE, support_handlers.handle_contact))
    
    # افزودن هندلر برای callback queries
    application.add_handler(CallbackQueryHandler(auth_handlers.handle_callback_query))
    
    # شروع ربات
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # اجرا در Railway با webhook
        port = int(os.environ.get("PORT", 8443))
        webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL')}.railway.app/{BOT_TOKEN}"
        
        logger.info(f"Starting webhook on port {port}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            secret_token="WEBHOOK_SECRET"
        )
    else:
        # اجرا به صورت محلی با polling
        logger.info("Starting polling locally")
        application.run_polling()

if __name__ == "__main__":
    main()