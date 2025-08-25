from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session
from models.database import User, get_db
import utils.helpers as helpers
import utils.validators as validators
import config.config as config

async def start_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # بررسی آیا کاربر قبلاً تأیید شده است
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user and user.is_verified:
        await update.message.reply_text("شما قبلاً احراز هویت شده‌اید و می‌توانید در گروه فعالیت کنید.")
        return ConversationHandler.END
    
    # اگر کاربر وجود ندارد، ایجاد کنید
    if not user:
        user = User(
            user_id=user_id,
            username=update.message.from_user.username,
            first_name=update.message.from_user.first_name,
            is_verified=False
        )
        db.add(user)
        db.commit()
    
    # درخواست نام و نام خانوادگی
    await update.message.reply_text("لطفاً نام و نام خانوادگی خود را وارد کنید:")
    helpers.set_user_state(user_id, config.AWAITING_NAME)
    return config.AWAITING_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    full_name = update.message.text
    
    if not validators.validate_name(full_name):
        await update.message.reply_text("لطفاً یک نام معتبر وارد کنید (فقط حروف و فاصله مجاز است):")
        return config.AWAITING_NAME
    
    # ذخیره نام در دیتابیس
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    user.first_name = full_name.split()[0] if full_name.split() else ""
    user.last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
    db.commit()
    
    # درخواست شماره تلفن
    keyboard = [[KeyboardButton("اشتراک گذاری شماره تلفن", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "لطفاً شماره تلفن خود را به اشتراک بگذارید:",
        reply_markup=reply_markup
    )
    
    helpers.set_user_state(user_id, config.AWAITING_PHONE)
    return config.AWAITING_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
    
    if not validators.validate_phone(phone_number):
        await update.message.reply_text("لطفاً یک شماره تلفن معتبر وارد کنید:")
        return config.AWAITING_PHONE
    
    # ذخیره شماره تلفن در دیتابیس
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    user.phone = phone_number
    db.commit()
    
    # درخواست اسکرین‌شات اول
    await update.message.reply_text(
        "لطفاً بخش اول اسکرین‌شات مربوط به سایت مسکن ملی را ارسال کنید:",
        reply_markup=ReplyKeyboardMarkup([["انصراف"]], resize_keyboard=True)
    )
    
    helpers.set_user_state(user_id, config.AWAITING_SCREENSHOT_1)
    return config.AWAITING_SCREENSHOT_1

async def get_screenshot_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند احراز هویت لغو شد.")
        helpers.delete_user_state(user_id)
        return ConversationHandler.END
    
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک تصویر ارسال کنید:")
        return config.AWAITING_SCREENSHOT_1
    
    # ذخیره اسکرین‌شات اول
    photo_id = update.message.photo[-1].file_id
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    user.screenshot_1 = photo_id
    db.commit()
    
    # درخواست اسکرین‌شات دوم
    await update.message.reply_text("لطفاً بخش دوم اسکرین‌شات مربوط به سایت مسکن ملی را ارسال کنید:")
    
    helpers.set_user_state(user_id, config.AWAITING_SCREENSHOT_2)
    return config.AWAITING_SCREENSHOT_2

async def get_screenshot_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند احراز هویت لغو شد.")
        helpers.delete_user_state(user_id)
        return ConversationHandler.END
    
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک تصویر ارسال کنید:")
        return config.AWAITING_SCREENSHOT_2
    
    # ذخیره اسکرین‌شات دوم
    photo_id = update.message.photo[-1].file_id
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    user.screenshot_2 = photo_id
    db.commit()
    
    # ارسال اطلاعات به ادمین
    await send_to_admin(update, context, user)
    
    await update.message.reply_text(
        "اطلاعات شما با موفقیت ثبت شد و برای تأیید به ادمین ارسال گردید. پس از تأیید، می‌توانید در گروه فعالیت کنید."
    )
    
    helpers.delete_user_state(user_id)
    return ConversationHandler.END

async def send_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    message_text = f"""
📋 درخواست احراز هویت جدید:
    
👤 نام کاربر: {user.first_name} {user.last_name or ''}
📞 شماره تلفن: {user.phone}
🆔 آی‌دی کاربر: {user.user_id}
👤 نام کاربری: @{user.username or 'ندارد'}
    """
    
    for admin_id in config.ADMIN_IDS:
        try:
            # ارسال اطلاعات متنی
            await context.bot.send_message(admin_id, message_text)
            
            # ارسال اسکرین‌شات‌ها
            if user.screenshot_1:
                await context.bot.send_photo(admin_id, user.screenshot_1, caption="اسکرین‌شات بخش اول")
            if user.screenshot_2:
                await context.bot.send_photo(admin_id, user.screenshot_2, caption="اسکرین‌شات بخش دوم")
                
            # ارسال دکمه‌های تأیید/رد
            keyboard = [
                [{"text": "✅ تأیید عضویت", "callback_data": f"verify_{user.user_id}"}],
                [{"text": "❌ رد عضویت", "callback_data": f"reject_{user.user_id}"}]
            ]
            
            await context.bot.send_message(
                admin_id,
                "لطفاً درخواست کاربر را بررسی و اقدام مناسب را انتخاب کنید:",
                reply_markup={"inline_keyboard": keyboard}
            )
        except Exception as e:
            print(f"Error sending message to admin {admin_id}: {e}")

async def cancel_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    helpers.delete_user_state(user_id)
    await update.message.reply_text("فرآیند احراز هویت لغو شد.")
    return ConversationHandler.END