from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from sqlalchemy.orm import Session
from models.database import User, AdminMessage, Session
from config.config import ADMIN_IDS, GROUP_ID
from datetime import datetime

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not ADMIN_IDS or user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📋 لیست اعضا", callback_data="members_list")],
        [InlineKeyboardButton("🖼 مدیریت عکس‌های راهنما", callback_data="manage_guide_images")],
        [InlineKeyboardButton("📊 آمار ربات", callback_data="bot_stats")],
        [InlineKeyboardButton("🔍 درخواست‌های pending", callback_data="pending_requests")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👨‍💼 پنل مدیریت ربات:\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def members_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not ADMIN_IDS or user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    db_session = Session()
    verified_users = db_session.query(User).filter(User.is_verified == True).all()
    
    if not verified_users:
        await update.message.reply_text("هیچ عضو تأیید شده‌ای وجود ندارد.")
        db_session.close()
        return
    
    # تقسیم لیست به بخش‌های کوچکتر برای جلوگیری از محدودیت طول پیام
    for i in range(0, len(verified_users), 20):
        user_batch = verified_users[i:i+20]
        verified_text = "✅ اعضای تأیید شده:\n\n"
        for j, user in enumerate(user_batch, i+1):
            verified_text += f"{j}. {user.first_name} {user.last_name or ''} - @{user.username or 'بدون نام کاربری'}\n"
        await update.message.reply_text(verified_text)
    
    db_session.close()

async def pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not ADMIN_IDS or user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    db_session = Session()
    pending_users = db_session.query(User).filter(User.verification_requested == True, User.is_verified == False).all()
    
    if not pending_users:
        await update.message.reply_text("هیچ درخواست pendingی وجود ندارد.")
        db_session.close()
        return
    
    for user in pending_users:
        # ایجاد دکمه‌های فوری برای هر کاربر
        keyboard = [
            [
                InlineKeyboardButton(f"✅ تأیید {user.first_name}", callback_data=f"verify_{user.user_id}"),
                InlineKeyboardButton(f"❌ رد {user.first_name}", callback_data=f"reject_{user.user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"کاربر: {user.first_name}\nتلفن: {user.phone_number}\n",
            reply_markup=reply_markup
        )
    
    db_session.close()

# ... (بقیه توابع بدون تغییر، فقط شرط if not ADMIN_IDS اضافه شود)

# این تابع اضافه شده است - برای حل خطای AttributeError
def callback_query_handler():
    return CallbackQueryHandler(handle_admin_callback)