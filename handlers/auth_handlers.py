from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackContext
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import filters
from database import Session, User
from config import ADMIN_IDS

# مراحل احراز هویت
(
    START,
    GET_NAME,
    GET_PHONE,
    GET_SCREENSHOT1,
    GET_SCREENSHOT2,
    CONFIRMATION
) = range(6)

def setup_auth_handlers(dp):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            GET_SCREENSHOT1: [MessageHandler(filters.PHOTO, get_screenshot1)],
            GET_SCREENSHOT2: [MessageHandler(filters.PHOTO, get_screenshot2)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('help', help_command))

# بقیه توابع بدون تغییر می‌مانند...