from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config.config import ADMIN_IDS
from models.database import Session, User

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 راهنمای ربات احراز هویت گروه مسکن ملی پویان بتن نیشابور:\n\n"
        "1. برای شروع فرآیند احراز هویت، از دستور /verify استفاده کنید.\n"
        "2. مراحل احراز هویت شامل وارد کردن نام، شماره تلفن و ارسال اسکرین شات‌ها می‌باشد.\n"
        "3. پس از تأیید اطلاعات توسط ادمین، شما می‌توانید در گروه فعالیت کنید.\n"
        "4. در صورت بروز هرگونه مشکل، از دستور /support استفاده کنید.\n\n"
        "⚠️ لطفاً توجه داشته باشید که تا زمان تکمیل فرآیند احراز هویت، امکان ارسال بیش از ۳ پیام در گروه را ندارید."
    )
    
    await update.message.reply_text(help_text)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = (
        "🆘 پشتیبانی ربات:\n\n"
        "در صورت بروز هرگونه مشکل یا سؤال، لطفاً با ادمین‌های گروه تماس بگیرید.\n"
        "یا پیام خود را از این طریق ارسال کنید که به ادمین‌ها转发 خواهد شد."
    )
    
    # ایجاد دکمه برای تماس با پشتیبانی
    contact_keyboard = [[KeyboardButton("📞 تماس با پشتیبانی", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(support_text, reply_markup=reply_markup)

async def forward_to_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text
    
    # بررسی آیا کاربر در دیتابیس وجود دارد
    db_session = Session()
    user_data = db_session.query(User).filter(User.user_id == user.id).first()
    db_session.close()
    
    user_status = "✅ تأیید شده" if user_data and user_data.is_verified else "⏳ در انتظار تأیید" if user_data else "❌ ناشناس"
    
    # ارسال پیام به تمام ادمین‌ها
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"📩 پیام پشتیبانی:\n\n"
                    f"👤 از: {user.first_name} {user.last_name or ''} (@{user.username or 'بدون نام کاربری'})\n"
                    f"🆔 آیدی: {user.id}\n"
                    f"✅ وضعیت: {user_status}\n\n"
                    f"📝 پیام:\n{message_text}"
                )
            )
        except Exception as e:
            print(f"Error forwarding message to admin {admin_id}: {e}")
    
    await update.message.reply_text("✅ پیام شما به پشتیبانی ارسال شد. به زودی با شما تماس خواهند گرفت.")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت اطلاعات تماس ارسال شده توسط کاربر"""
    if update.message.contact:
        contact = update.message.contact
        user = update.effective_user
        
        # ذخیره اطلاعات تماس در دیتابیس
        db_session = Session()
        user_data = db_session.query(User).filter(User.user_id == user.id).first()
        
        if user_data:
            user_data.phone_number = contact.phone_number
            db_session.commit()
        
        db_session.close()
        
        # ارسال اطلاعات تماس به ادمین‌ها
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"📞 کاربر درخواست تماس کرده:\n\n"
                        f"👤 نام: {user.first_name} {user.last_name or ''}\n"
                        f"📛 نام در مخاطب: {contact.first_name} {contact.last_name or ''}\n"
                        f"📞 تلفن: {contact.phone_number}\n"
                        f"🆔 آیدی: {user.id}"
                    )
                )
            except Exception as e:
                print(f"Error sending contact to admin {admin_id}: {e}")
        
        await update.message.reply_text("✅ اطلاعات تماس شما دریافت شد. به زودی با شما تماس خواهیم گرفت.")