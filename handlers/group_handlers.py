from telegram.ext import MessageHandler, Filters, CallbackContext
from telegram import Update, ChatPermissions
from datetime import datetime, timedelta
import pytz

from database import Session, User
from config import MAX_MESSAGES_BEFORE_VERIFICATION, TEMPORARY_BAN_MINUTES

def setup_group_handlers(dp):
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_new_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, goodbye_member))
    dp.add_handler(MessageHandler(Filters.chat_type.groups & Filters.text & Filters.regex(r'^(سلام|سلام علیکم|سلام بر شما|سلام به همه)'), reply_to_salam))
    dp.add_handler(MessageHandler(Filters.chat_type.groups & ~Filters.status_update, count_user_messages))

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
    reply_text = f"سلام {user.first_name} عزیز 🙏\nچطور می‌تونم کمکتون کنم؟"
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
        
        if db_user.message_count >= MAX_MESSAGES_BEFORE_VERIFICATION:
            # محدود کردن کاربر
            until_date = datetime.now(pytz.utc) + timedelta(minutes=TEMPORARY_BAN_MINUTES)
            context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            
            # اعلام مسدودیت
            warning_msg = f"⚠️ کاربر {user.first_name} به دلیل عدم تکمیل احراز هویت به صورت موقت مسدود شد.\nلطفاً برای فعال شدن، از طریق ربات احراز هویت کنید."
            update.message.reply_text(warning_msg)
            
            # ریست کردن شمارنده پیام
            db_user.message_count = 0
            db_user.is_banned = True
            session.commit()
    
    session.close()