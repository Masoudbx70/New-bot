from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters
from database import Session, User

def setup_admin_handlers(dp):
    dp.add_handler(CommandHandler('admin', admin_panel))
    dp.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^admin_'))
    dp.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handle_admin_photo))

# بقیه توابع بدون تغییر می‌مانند...