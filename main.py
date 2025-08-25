import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv

import config.config as config
from handlers import group_handlers, auth_handlers, admin_handlers, support_handlers

# بارگذاری متغیرهای محیطی
load_dotenv()

def main():
    # ایجاد برنامه‌ی ربات
    application = Application.builder().token(config.TOKEN).build()
    
    # افزودن هندلرهای گروه
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_handlers.welcome_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_handlers.farewell_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_handlers.respond_to_greeting))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, group_handlers.monitor_messages))
    
    # افزودن هندلرهای احراز هویت
    auth_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('auth', auth_handlers.start_auth)],
        states={
            config.AWAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_handlers.get_name)],
            config.AWAITING_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), auth_handlers.get_phone)],
            config.AWAITING_SCREENSHOT_1: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), auth_handlers.get_screenshot_1)],
            config.AWAITING_SCREENSHOT_2: [MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), auth_handlers.get_screenshot_2)],
        },
        fallbacks=[CommandHandler('cancel', auth_handlers.cancel_auth)],
    )
    application.add_handler(auth_conv_handler)
    
    # افزودن هندلرهای ادمین
    application.add_handler(CommandHandler('admin', admin_handlers.admin_panel))
    application.add_handler(CallbackQueryHandler(admin_handlers.handle_admin_callback))
    
    # افزودن هندلرهای پشتیبانی
    application.add_handler(CommandHandler('support', support_handlers.support))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, support_handlers.handle_support_message))
    
    # شروع ربات
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('WEBHOOK_MODE', 'false').lower() == 'true':
        # در Railway از وب‌هوک استفاده کنید
        port = int(os.getenv('PORT', 8443))
        webhook_url = os.getenv('WEBHOOK_URL')
        token = config.TOKEN
        
        if webhook_url:
            # تنظیم وب‌هوک
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=token,
                webhook_url=f"{webhook_url.rstrip('/')}/{token}",
                cert=os.getenv('SSL_CERT'),  # در صورت استفاده از SSL
                key=os.getenv('SSL_KEY'),   # در صورت استفاده از SSL
            )
            print(f"Bot is running in webhook mode on {webhook_url}")
        else:
            print("Warning: WEBHOOK_URL not set. Using polling instead.")
            application.run_polling()
    else:
        # در محیط توسعه از polling استفاده کنید
        print("Bot is running in polling mode")
        application.run_polling()

if __name__ == '__main__':
    main()