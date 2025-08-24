import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
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
    
    # شروع ربات
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # اجرا در Railway
        url = os.environ.get('RAILWAY_STATIC_URL', '').replace('https://', '')
        webhook_url = f"https://{url}/webhook" if url else None
        
        if webhook_url:
            application.run_webhook(
                listen="0.0.0.0",
                port=int(os.environ.get("PORT", 8443)),
                url_path="webhook",
                webhook_url=webhook_url,
                drop_pending_updates=True
            )
        else:
            application.run_polling()
    else:
        # اجرا به صورت محلی
        application.run_polling()

if __name__ == "__main__":
    main()