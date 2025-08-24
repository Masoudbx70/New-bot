from telegram.ext import MessageHandler, CallbackContext
from telegram import Update, ChatPermissions
from datetime import datetime, timedelta
import pytz
from telegram.ext import filters

from database import Session, User
from config import MAX_MESSAGES_BEFORE_VERIFICATION, TEMPORARY_BAN_MINUTES

def setup_group_handlers(dp):
    dp.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    dp.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))
    dp.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.Text(["سلام", "سلام علیکم", "سلام بر شما", "سلام به همه"]), reply_to_salam))
    dp.add_handler(MessageHandler(filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL, count_user_messages))

def welcome_new_member(update: Update, context: CallbackContext):
    for new_member in update.message.new_chat_members:
        if new_member.is_bot and new_member.id == context.bot.id:
            # ربات به گروه اضافه شده
            update.message.reply_text("سلام! من ربات مدیریت گروه مسکن ملی پویان بتن نیشابور هستم. برای اطلاعات بیشتر /help رو بفرستید.")
        else:
            # کاربر جدید به گروه اضافه شده
            session = Session()
            user = session.query(User).filter(User.user_id == new_member.id).first()
            
            if user and user.is_verified:
                welcome_msg = f"سلام {new_member.first_name}!\nبه گروه مسکن ملی پویان بتن نیشابور خوش آمدی!"
            else:
                welcome_msg = f"سلام {new_member.first_name}!\nبه گروه مسکن ملی پویان بتن نیشابور خوش آمدی!\nلطفاً برای فعال شدن کامل در گروه، ابتدا از طریق ربات احراز هویت کنید. برای شروع /start رو بفرستید."
            
            update.message.reply_text(welcome_msg)
            session.close()

def goodbye_member(update: Update, context: CallbackContext):
    left_member = update.message.left_chat_member
    farewell_msg = f"👋 {left_member.first_name} از گروه ما رفت. امیدواریم باز هم به ما بپیوندی."
    update.message.reply_text(farewell_msg)

def reply_to_salam(update: Update, context: CallbackContext):
    user = update.effective_user
    reply_text = f"سلام {user.first_name} عزیز 🙏\nچطور می‌تونم کمکتون کنم?"
    update.message.reply_text(reply_text)

def count_user_messages(update: Update, context: CallbackContext):
    user = update.effective_user
    chat = update.effective_chat
    
    session = Session()
    db_user = session.query(User).filter(User.user_id == user.id).first()
    
    if not db_user or not db_user.is_verified:
        if not db_user:
            # کاربر جدید در دیتابیس
            db_user = User(
                user_id=user.id,
                chat_id=chat.id,
                first_name=user.first_name,
                last_name=user.last_name or ""
            )
            session.add(db_user)
        
        db_user.message_count += 1
        session.commit()
        
        if db_user.message_count >= MAX_MESSAGES_B