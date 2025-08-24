from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from models.database import User, AdminMessage, Session
from config.config import ADMIN_IDS, GROUP_ID
from datetime import datetime

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
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
    if user.id not in ADMIN_IDS:
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
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    db_session = Session()
    pending_users = db_session.query(User).filter(User.verification_requested == True, User.is_verified == False).all()
    
    if not pending_users:
        await update.message.reply_text("هیچ درخواست pendingی وجود ندارد.")
        db_session.close()
        return
    
    pending_text = "⏳ درخواست‌های pending:\n\n"
    
    for i, user in enumerate(pending_users, 1):
        pending_text += f"{i}. {user.first_name} {user.last_name or ''} - @{user.username or 'بدون نام کاربری'}\n"
        
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

async def manage_guide_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📷 افزودن عکس راهنما", callback_data="add_guide_image")],
        [InlineKeyboardButton("✏️ ویرایش عکس راهنما", callback_data="edit_guide_image")],
        [InlineKeyboardButton("🗑 حذف عکس راهنما", callback_data="delete_guide_image")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🖼 مدیریت عکس‌های راهنما:\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    db_session = Session()
    total_users = db_session.query(User).count()
    verified_users = db_session.query(User).filter(User.is_verified == True).count()
    pending_users = db_session.query(User).filter(User.verification_requested == True, User.is_verified == False).count()
    
    stats_text = (
        f"📊 آمار ربات:\n\n"
        f"👥 کل کاربران: {total_users}\n"
        f"✅ کاربران تأیید شده: {verified_users}\n"
        f"⏳ درخواست‌های pending: {pending_users}\n"
        f"📅 تاریخ امروز: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    await update.message.reply_text(stats_text)
    db_session.close()

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "members_list":
        await members_list(update, context)
    elif query.data == "pending_requests":
        await pending_requests(update, context)
    elif query.data == "manage_guide_images":
        await manage_guide_images(update, context)
    elif query.data == "bot_stats":
        await bot_stats(update, context)
    elif query.data.startswith("verify_"):
        user_id = int(query.data.split("_")[1])
        await verify_user(update, context, user_id)
    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])
        await reject_user(update, context, user_id)
    elif query.data == "back_to_admin":
        await admin_panel(update, context)

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
                text="🎉 تبریک! احراز هویت شما تأیید شد!\n\nاکنون می‌توانید در گروه فعالیت کنید.\n\nاز بابت مسدودیت موقت پیش آمده پوزش می‌خواهیم."
            )
        except:
            pass  # اگر ربات نتواند به کاربر پیام بدهد
        
        # ارسال پیام خوش آمد به گروه
        try:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=f"🎊 کاربر {user.first_name} با موفقیت احراز هویت شد و به جمع ما پیوست! خوش آمدید."
            )
        except:
            pass  # اگر ربات نتواند در گروه پیام بدهد
        
        await update.callback_query.edit_message_text("✅ کاربر تأیید شد.")
    else:
        await update.callback_query.edit_message_text("❌ کاربر یافت نشد.")
    
    db_session.close()

async def reject_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    db_session = Session()
    user = db_session.query(User).filter(User.user_id == user_id).first()
    
    if user:
        # ارسال پیام رد درخواست به کاربر
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ متأسفانه درخواست احراز هویت شما رد شد.\n\nلطفاً با پشتیبانی تماس بگیرید."
            )
        except:
            pass  # اگر ربات نتواند به کاربر پیام بدهد
        
        db_session.delete(user)
        db_session.commit()
        
        await update.callback_query.edit_message_text("❌ درخواست کاربر رد شد.")
    else:
        await update.callback_query.edit_message_text("❌ کاربر یافت نشد.")
    
    db_session.close()