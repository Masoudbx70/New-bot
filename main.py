# main.py
import os
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from config.config import BOT_TOKEN
import handlers.group_handlers as group_handlers
import handlers.auth_handlers as auth_handlers
import handlers.admin_handlers as admin_handlers
import handlers.support_handlers as support_handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def build_application():
    application = Application.builder().token(BOT_TOKEN).build()

    # Group handlers (status & group messages)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_handlers.welcome_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_handlers.goodbye_member))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_handlers.handle_group_message))

    # Auth conversation handler (register the steps from auth_handlers)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('verify', auth_handlers.start_verification)],
        states={
            auth_handlers.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_handlers.handle_name)],
            auth_handlers.PHONE: [
                MessageHandler(filters.CONTACT, auth_handlers.handle_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, auth_handlers.handle_phone)
            ],
            auth_handlers.SCREENSHOT1: [MessageHandler(filters.PHOTO, auth_handlers.handle_screenshot1)],
            auth_handlers.SCREENSHOT2: [MessageHandler(filters.PHOTO, auth_handlers.handle_screenshot2)],
        },
        fallbacks=[CommandHandler('cancel', auth_handlers.cancel)],
        allow_reentry=True
    )
    application.add_handler(conv_handler)

    # Basic command handlers
    application.add_handler(CommandHandler("start", auth_handlers.start))
    application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    application.add_handler(CommandHandler("members_list", admin_handlers.members_list))
    application.add_handler(CommandHandler("help", support_handlers.help_command))
    application.add_handler(CommandHandler("support", support_handlers.support))

    # Support contact & forward handlers
    application.add_handler(MessageHandler(filters.CONTACT, support_handlers.handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, support_handlers.forward_to_support))

    # CallbackQuery handlers (admin actions + auth callback)
    application.add_handler(CallbackQueryHandler(auth_handlers.handle_callback_query))
    application.add_handler(CallbackQueryHandler(admin_handlers.handle_admin_callback))

    return application

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Please set it in environment or .env.")
        return

    app = build_application()

    # Webhook config: flexible env var names
    webhook_base = os.environ.get("WEBHOOK_BASE_URL") or os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("RAILWAY_SERVICE_URL") or os.environ.get("WEBHOOK_URL")
    PORT = int(os.environ.get("PORT", "8443"))

    if webhook_base:
        webhook_base = webhook_base.rstrip('/')
        logger.info(f"Starting webhook at {webhook_base}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{webhook_base}/{BOT_TOKEN}"
        )
    else:
        logger.info("Starting polling (no webhook base found).")
        app.run_polling()

if __name__ == "__main__":
    main()