# handlers/auth_handlers.py
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from models.database import User, SessionLocal
from config.config import ADMIN_IDS, GROUP_ID
from utils.helpers import validate_phone_number, validate_name
import re

# مراحل احراز هویت
NAME, PHONE, SCREENSHOT1, SCREENSHOT2 = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"سلام {user.first_name}!\n"
        "به ربات احراز هویت خوش آمدید.\n"
        "برای شروع فرآیند احراز هویت، از دستور /verify استفاده کنید.\n\n"
        "برای راهنمایی بیشتر از دستور /help استفاده کنید."
    )

async def start_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = SessionLocal()
    try:
        user_data = db.query(User).filter(User.user_id == user.id).first()

        if user_data and user_data.is_verified:
            await update.message.reply_text("شما قبلاً احراز هویت شده‌اید.")
            return ConversationHandler.END

        # از نو شروع کردن فرآیند
        context.user_data.clear()

        if not user_data:
            user_data = User(user_id=user.id, username=user.username, first_name=user.first_name)
            db.add(user_data)
            db.commit()
        await update.message.reply_text(
            "فرآیند احراز هویت شروع شد.\nلطفاً نام و نام خانوادگی خود را وارد کنید:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME
    finally:
        db.close()

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not validate_name(name):
        await update.message.reply_text("لطفاً یک نام معتبر وارد کنید (حداقل ۳ حرف):")
        return NAME

    context.user_data['name'] = name
    contact_keyboard = [[KeyboardButton("اشتراک گذاری شماره تلفن", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("لطفاً شماره تلفن خود را به اشتراک بگذارید:", reply_markup=reply_markup)
    return PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
        if not validate_phone_number(phone_number):
            await update.message.reply_text("لطفاً یک شماره تلفن معتبر وارد کنید (مثال: 09123456789):")
            return PHONE

    context.user_data['phone'] = phone_number
    db = SessionLocal()
    try:
        user = update.effective_user
        user_data = db.query(User).filter(User.user_id == user.id).first()
        if user_data:
            # تقسیم نام به نام و نام خانوادگی
            name_parts = context.user_data.get('name', '').split(' ', 1)
            user_data.first_name = name_parts[0] if name_parts else user.first_name
            user_data.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user_data.phone_number = phone_number
            db.commit()
    finally:
        db.close()

    await update.message.reply_text("لطفاً بخش اول اسکرین شات مربوط به سایت مسکن ملی را ارسال کنید:", reply_markup=ReplyKeyboardRemove())
    return SCREENSHOT1

async def handle_screenshot1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک تصویر ارسال کنید:")
        return SCREENSHOT1

    file_id = update.message.photo[-1].file_id
    context.user_data['screenshot1'] = file_id

    db = SessionLocal()
    try:
        user = update.effective_user
        user_data = db.query(User).filter(User.user_id == user.id).first()
        if user_data:
            user_data.screenshot1 = file_id
            db.commit()
    finally:
        db.close()

    await update.message.reply_text("لطفاً بخش دوم اسکرین شات مربوط به سایت مسکن ملی را ارسال کنید:")
    return SCREENSHOT2

async def handle_screenshot2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک تصویر ارسال کنید:")
        return SCREENSHOT2

    file_id = update.message.photo[-1].file_id
    context.user_data['screenshot2'] = file_id

    db = SessionLocal()
    try:
        user = update.effective_user
        user_data = db.query(User).filter(User.user_id == user.id).first()
        if user_data:
            user_data.screenshot2 = file_id
            user_data.verification_requested = True
            db.commit()
    finally:
        db.close()

    # ارسال اطلاعات به ادمین‌ها
    await send_verification_to_admin(update, context)

    await update.message.reply_text(
        "✅ اطلاعات شما با موفقیت ثبت شد و برای بررسی به ادمین ارسال گردید.\n"
        "پس از تأیید، شما می‌توانید در گروه فعالیت کنید.\n\n"
        "برای پیگیری وضعیت می‌توانید با ادمین ها در ارتباط باشید."
    )
    return ConversationHandler.END

async def send_verification_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = context.user_data.get('name', '')
    phone = context.user_data.get('phone', '')
    screenshot1 = context.user_data.get('screenshot1', '')
    screenshot2 = context.user_data.get('screenshot2', '')

    message_text = (
        f"📋 درخواست احراز هویت جدید:\n\n"
        f"👤 کاربر: {user.first_name} {user.last_name or ''} (@{user.username or 'بدون نام کاربری'})\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"📛 نام کامل: {name}\n"
        f"📞 شماره تلفن: {phone}\n\n"
        f"لطفاً تأیید یا رد کنید:"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید عضویت", callback_data=f"verify_{user.id}"),
            InlineKeyboardButton("❌ رد عضویت", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(chat_id=admin_id, photo=screenshot1, caption=message_text, reply_markup=reply_markup)
            if screenshot2:
                await context.bot.send_photo(chat_id=admin_id, photo=screenshot2, caption="اسکرین شات دوم")
        except Exception as e:
            print(f"Error sending message to admin {admin_id}: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند احراز هویت لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# هندلر callback برای دکمه‌های تأیید/رد که توسط admin یا auth فرستاده شده
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    # از admin_handlers فانکشن‌ها را صدا می‌زنیم
    from handlers.admin_handlers import verify_user as admin_verify_user, reject_user as admin_reject_user

    if data.startswith("verify_"):
        user_id = int(data.split("_", 1)[1])
        await admin_verify_user(update, context, user_id)
    elif data.startswith("reject_"):
        user_id = int(data.split("_", 1)[1])
        await admin_reject_user(update, context, user_id)