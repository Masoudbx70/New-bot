from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from models.database import User, AdminMessage, Session
from config.config import ADMIN_IDS, GROUP_ID

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    keyboard = [
        [InlineKeyboardButton("لیست اعضا", callback_data="members_list")],
        [InlineKeyboardButton("مدیریت عکس‌های راهنما", callback_data="manage_guide_images")],
        [InlineKeyboardButton("آمار ربات", callback_data="bot_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "پنل مدیریت ربات:\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def members_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    db_session = Session()
    verified_users = db_session.query(User).filter(User.is_verified == True).all()
    pending_users = db_session.query(User).filter(User.verification_requested == True, User.is_verified == False).all()
    
    verified_text = "اعضای تأیید شده:\n\n"
    for i, user in enumerate(verified_users, 1):
        verified_text += f"{i}. {user.first_name} {user.last_name or ''} - @{user.username or 'بدون نام کاربری'}\n"
    
    pending_text = "درخواست‌های pending:\n\n"
    for i, user in enumerate(pending_users, 1):
        pending_text += f"{i}. {user.first_name} {user.last_name or ''} - @{user.username or 'بدون نام کاربری'}\n"
    
    db_session.close()
    
    await update.message.reply_text(verified_text)
    await update.message.reply_text(pending_text)

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "members_list":
        await members_list_callback(update, context)
    elif query.data.startswith("verify_"):
        user_id = int(query.data.split("_")[1])
        await verify_user(update, context, user_id)
    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        await reject_user(update, context, user_id)
    elif query.data == "manage_guide_images":
        await manage_guide_images(update, context)

async def verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    db_session = Session()
    user = db_session.query(User).filter(User.user_id == user_id).first()
    
    if user:
        user.is_verified = True
        user.verified_at = datetime.now()
        db_session.commit()
        
        # ارسال پیام تبریک به کاربر
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="احراز هویت شما تأیید شد! اکنون می‌توانید در گروه فعالیت کنید.\n\nاز بابت مسدودیت موقت پیش آمده پوزش می‌خواهیم."
            )
        except:
            pass  # اگر ربات نتواند به کاربر پیام بدهد
        
        # ارسال پیام خوش آمد به گروه
        try:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=f"کاربر {user.first_name} با موفقیت احراز هویت شد و به جمع ما پیوست! خوش آمدید."
            )
        except:
            pass  # اگر ربات نتواند در گروه پیام بدهد
        
        await update.callback_query.edit_message_text("کاربر تأیید شد.")
    else:
        await update.callback_query.edit_message_text("کاربر یافت نشد.")
    
    db_session.close()

async def reject_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    db_session = Session()
    user = db_session.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # ارسال پیام رد درخواست به کاربر
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="متأسفانه درخواست احراز هویت شما رد شد. لطفاً با پشتیبانی تماس بگیرید."
            )
        except:
            pass  # اگر ربات نتواند به کاربر پیام بدهد
        
        db_session.delete(user)
        db_session.commit()
        
        await update.callback_query.edit_message_text("درخواست کاربر رد شد.")
    else:
        await update.callback_query.edit_message_text("کاربر یافت نشد.")
    
    db_session.close()