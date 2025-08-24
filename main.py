import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import group_handlers, auth_handlers, admin_handlers, support_handlers

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن متغیرهای محیطی مستقیماً
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',')] if ADMIN_IDS_STR else []
GROUP_ID_STR = os.getenv("GROUP_ID", "")
GROUP_ID = int(GROUP_ID_STR) if GROUP_ID_STR.isdigit() else None
DATABASE_URL = os.getenv("DATABASE_URL")

# سایر تنظیمات
MAX_MESSAGES_BEFORE_VERIFICATION = 3
TEMPORARY_BAN_DURATION = 3600  # 1 ساعت به ثانیه

# بررسی تنظیمات ضروری
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")

if not ADMIN_IDS:
    print("Warning: ADMIN_IDS is empty. Admin features will not work.")

if not GROUP_ID:
    print("Warning: GROUP_ID is not set. Group features will not work.")

def main():
    # ایجاد برنامه
    application = Application.builder().token(BOT_TOKEN).build()
    
    # افزودن هندلرهای گروه
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_handlers.welcome_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_handlers.goodbye_member))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_handlers.handle_group_message))
    
    # افزودن هندلرهای احراز هویت (ConversationHandler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("verify", auth_handlers.start_verification)],
        states={
            auth_handlers.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_handlers.handle_name)],
            auth_handlers.PHONE: [
                MessageHandler(filters.CONTACT, auth_handlers.handle_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, auth_handlers.handle_phone)
            ],
            auth_handlers.SCREENSHOT1: [MessageHandler(filters.PHOTO, auth_handlers.handle_screenshot1)],
            auth_handlers.SCREENSHOT2: [MessageHandler(filters.PHOTO, auth_handlers.handle_screenshot2)]
        },
        fallbacks=[CommandHandler("cancel", auth_handlers.cancel)]
    )
    application.add_handler(conv_handler)
    
    # افزودن سایر هندلرها
    application.add_handler(CommandHandler("start", auth_handlers.start))
    application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    application.add_handler(CommandHandler("members_list", admin_handlers.members_list))
    application.add_handler(CommandHandler("help", support_handlers.help_command))
    application.add_handler(CommandHandler("support", support_handlers.support))
    
    # افزودن هندلر برای callback queries
    application.add_handler(admin_handlers.callback_query_handler())
    
    # افزودن هندلر برای پیام‌های پشتیبانی
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, support_handlers.forward_to_support))
    application.add_handler(MessageHandler(filters.CONTACT & filters.ChatType.PRIVATE, support_handlers.handle_contact))
    
    # شروع ربات
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_GIT_COMMIT_SHA'):
        # اجرا در Railway
        port = int(os.environ.get("PORT", 8443))
        webhook_url = os.environ.get('RAILWAY_STATIC_URL')
        
        if webhook_url:
            # حذف https:// از ابتدای URL اگر وجود دارد
            if webhook_url.startswith('https://'):
                webhook_url = webhook_url[8:]
            
            full_webhook_url = f"https://{webhook_url}/webhook"
            
            # تنظیم webhook قبل از اجرا
            async def set_webhook():
                await application.bot.set_webhook(url=full_webhook_url)
            
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                webhook_url=full_webhook_url,
                url_path="webhook",
                drop_pending_updates=True
            )
        else:
            # اگر webhook_url وجود ندارد، از polling استفاده کن
            application.run_polling()
    else:
        # اجرا به صورت محلی
        application.run_polling()

if __name__ == "__main__":
    main()