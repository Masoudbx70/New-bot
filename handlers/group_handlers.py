from telegram import Update, Bot
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from models.database import User, get_db
import utils.helpers as helpers
import config.config as config

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for new_member in update.message.new_chat_members:
        user_id = new_member.id
        first_name = new_member.first_name
        
        # بررسی آیا کاربر در دیتابیس وجود دارد و تأیید شده است
        db = next(get_db())
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if user and user.is_verified:
            welcome_message = f"سلام {first_name}!\nبه گروه مسکن ملی پویان بتن نیشابور خوش آمدید!"
            await update.message.reply_text(welcome_message)
        else:
            welcome_message = f"سلام {first_name}!\nبه گروه مسکن ملی پویان بتن نیشابور خوش آمدید!\nلطفاً برای فعالیت در گروه، ابتدا از طریق ربات احراز هویت کنید."
            await update.message.reply_text(welcome_message)
            
            # اگر کاربر وجود ندارد، یک رکورد جدید ایجاد کنید
            if not user:
                new_user = User(
                    user_id=user_id,
                    username=new_member.username,
                    first_name=first_name,
                    is_verified=False
                )
                db.add(new_user)
                db.commit()

async def farewell_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    farewell_message = f"خدانگهدار {left_member.first_name}!\nامیدواریم باز هم به ما بپیوندید."
    await update.message.reply_text(farewell_message)

async def respond_to_greeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.lower()
    greetings = ['سلام', 'hello', 'hi', 'سلامونک', 'slm', 'salam']
    
    if any(greeting in message_text for greeting in greetings):
        user = update.message.from_user
        response = f"سلام {user.first_name} عزیز! خوش آمدید. 😊"
        await update.message.reply_text(response)

async def monitor_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    
    # اگر کاربر ادمین است، نیاز به بررسی ندارد
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user and user.is_admin:
        return
    
    # اگر کاربر تأیید نشده است
    if not user or not user.is_verified:
        message_count = helpers.increment_message_count(user_id)
        
        if message_count == 1:
            warning = "کاربر عزیز، لطفاً برای ادامه فعالیت در گروه، از طریق ربات احراز هویت کنید."
            await update.message.reply_text(warning)
        elif message_count == 2:
            warning = "این دومین اخطار شماست. پس از یک اخطار دیگر، به طور موقت از گروه حذف خواهید شد."
            await update.message.reply_text(warning)
        elif message_count >= 3:
            # حذف کاربر از گروه
            try:
                await context.bot.ban_chat_member(chat_id, user_id, until_date=60)  # مسدود به مدت 1 دقیقه
                await update.message.reply_text(f"کاربر {update.message.from_user.first_name} به دلیل عدم احراز هویت به طور موقت از گروه حذف شد.")
                helpers.reset_message_count(user_id)
            except Exception as e:
                print(f"Error banning user: {e}")