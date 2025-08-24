# handlers/admin_handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.database import User, AdminMessage, SessionLocal
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
    await update.message.reply_text("👨‍💼 پنل مدیریت ربات:\nلطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

async def members_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return

    db = SessionLocal()
    try:
        verified_users = db.query(User).filter(User.is_verified == True).all()
        if not verified_users:
            await update.message.reply_text("هیچ عضو تأیید شده‌ای وجود ندارد.")
            return

        for i in range(0, len(verified_users), 20):
            batch = verified_users[i:i+20]
            text = "✅ اعضای تأیید شده:\n\n"
            for j, u in enumerate(batch, i+1):
                text += f"{j}. {u.first_name} {u.last_name or ''} - @{u.username or 'بدون نام کاربری'}\n"
            await update.message.reply_text(text)
    finally:
        db.close()

# بقیه توابع مشابه: pending_requests, manage_guide_images, bot_stats
async def pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return

    db = SessionLocal()
    try:
        pending_users = db.query(User).filter(User.verification_requested == True, User.is_verified == False).all()
        if not pending_users:
            await update.message.reply_text("هیچ درخواست pendingی وجود ندارد.")
            return

        for u in pending_users:
            keyboard = [
                [
                    InlineKeyboardButton(f"✅ تأیید {u.first_name}", callback_data=f"verify_{u.user_id}"),
                    InlineKeyboardButton(f"❌ رد {u.first_name}", callback_data=f"reject_{u.user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"کاربر: {u.first_name}\nتلفن: {u.phone_number or 'ثبت نشده'}\n", reply_markup=reply_markup)
    finally:
        db.close()

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
    await update.message.reply_text("🖼 مدیریت عکس‌های راهنما:\nلطفاً یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        pending_users = db.query(User).filter(User.verification_requested == True, User.is_verified == False).count()
        stats_text = (
            f"📊 آمار ربات:\n\n"
            f"👥 کل کاربران: {total_users}\n"
            f"✅ کاربران تأیید شده: {verified_users}\n"
            f"⏳ درخواست‌های pending: {pending_users}\n"
            f"📅 تاریخ امروز: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        await update.message.reply_text(stats_text)
    finally:
        db.close()

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if data == "members_list":
        await members_list(update, context)
    elif data == "pending_requests":
        await pending_requests(update, context)
    elif data == "manage_guide_images":
        await manage_guide_images(update, context)
    elif data == "bot_stats":
        await bot_stats(update, context)
    elif data.startswith("verify_"):
        user_id = int(data.split("_", 1)[1])
        await verify_user(update, context, user_id)
    elif data.startswith("reject_"):
        user_id = int(data.split("_", 1)[1])
        await reject_user(update, context, user_id)
    elif data == "back_to_admin":
        await admin_panel(update, context)

async def verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            db.commit()
            try:
                await context.bot.send_message(chat_id=user_id, text="🎉 تبریک! احراز هویت شما تأیید شد!")
            except:
                pass
            try:
                await context.bot.send_message(chat_id=GROUP_ID, text=f"🎊 کاربر {user.first_name} با موفقیت احراز هویت شد! خوش آمدید.")
            except:
                pass
            # ویرایش متن پیام callback
            try:
                await update.callback_query.edit_message_text("✅ کاربر تأیید شد.")
            except:
                pass
        else:
            try:
                await update.callback_query.edit_message_text("❌ کاربر یافت نشد.")
            except:
                pass
    finally:
        db.close()

async def reject_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            try:
                await context.bot.send_message(chat_id=user_id, text="❌ متأسفانه درخواست احراز هویت شما رد شد.")
            except:
                pass
            db.delete(user)
            db.commit()
            try:
                await update.callback_query.edit_message_text("❌ درخواست کاربر رد شد.")
            except:
                pass
        else:
            try:
                await update.callback_query.edit_message_text("❌ کاربر یافت نشد.")
            except:
                pass
    finally:
        db.close()