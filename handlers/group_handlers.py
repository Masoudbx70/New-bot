from telegram import Update, Bot
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from models.database import User, Session
from config.config import GROUP_ID, MAX_MESSAGES_BEFORE_VERIFICATION, TEMPORARY_BAN_DURATION
from utils.helpers import is_user_verified

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return
    
    for new_member in update.message.new_chat_members:
        if new_member.is_bot and new_member.id == context.bot.id:
            await update.message.reply_text("سلام! من ربات مدیریت گروه مسکن ملی پویان بتن نیشابور هستم. برای احراز هویت، پیام خصوصی برام بفرستید.")
            return
        
        # بررسی آیا کاربر قبلاً احراز هویت شده
        db_session = Session()
        user = db_session.query(User).filter(User.user_id == new_member.id).first()
        
        if user and user.is_verified:
            welcome_text = f"خوش آمدید {new_member.first_name}!\nبه گروه مسکن ملی پویان بتن نیشابور خوش آمدید."
            await update.message.reply_text(welcome_text)
        else:
            warning_text = f"سلام {new_member.first_name}!\nلطفاً برای احراز هویت و فعال شدن در گروه، با ربات به صورت خصوصی ارتباط برقرار کنید."
            await update.message.reply_text(warning_text)
        
        db_session.close()

async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return
    
    left_member = update.message.left_chat_member
    goodbye_text = f"خدانگهدار {left_member.first_name}!\nامیدواریم باز هم به ما بپیوندید."
    await update.message.reply_text(goodbye_text)

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return
    
    user = update.effective_user
    message = update.effective_message
    
    # بررسی سلام کاربر و پاسخ دادن
    if message.text and any(greeting in message.text.lower() for greeting in ['سلام', 'سلامونک', 'hello', 'hi']):
        await message.reply_text(f"سلام {user.first_name} عزیز! خوش آمدید.")
    
    # بررسی وضعیت احراز هویت کاربر
    db_session = Session()
    user_data = db_session.query(User).filter(User.user_id == user.id).first()
    
    if not user_data or not user_data.is_verified:
        # اگر کاربر احراز هویت نکرده باشد
        if not user_data:
            user_data = User(user_id=user.id, username=user.username, first_name=user.first_name)
            db_session.add(user_data)
        
        user_data.message_count += 1
        db_session.commit()
        
        if user_data.message_count >= MAX_MESSAGES_BEFORE_VERIFICATION:
            # مسدود کردن کاربر پس از ۳ پیام
            try:
                until_date = int(update.message.date.timestamp()) + TEMPORARY_BAN_DURATION
                await context.bot.ban_chat_member(
                    chat_id=GROUP_ID,
                    user_id=user.id,
                    until_date=until_date
                )
                
                warning_message = f"کاربر {user.first_name} به دلیل عدم احراز هویت به طور موقت از گروه حذف شد.\nلطفاً برای احراز هویت با ربات در ارتباط باشید."
                await update.message.reply_text(warning_message)
                
                # ارسال پیام به کاربر
                try:
                    await context.bot.send_message(
                        chat_id=user.id,
                        text="شما به دلیل عدم احراز هویت از گروه حذف شدید. لطفاً برای احراز هویت و بازگشت به گروه، از دستور /verify استفاده کنید."
                    )
                except:
                    pass  # اگر ربات نتواند به کاربر پیام بدهد
                    
            except Exception as e:
                print(f"Error banning user: {e}")
    
    db_session.close()