from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackContext
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import filters
from models import Session, User
from config import ADMIN_IDS

# مراحل احراز هویت
(
    START,
    GET_NAME,
    GET_PHONE,
    GET_SCREENSHOT1,
    GET_SCREENSHOT2,
    CONFIRMATION
) = range(6)

def setup_auth_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            GET_SCREENSHOT1: [MessageHandler(filters.PHOTO, get_screenshot1)],
            GET_SCREENSHOT2: [MessageHandler(filters.PHOTO, get_screenshot2)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    
    session = Session()
    db_user = session.query(User).filter(User.user_id == user.id).first()
    
    if db_user and db_user.is_verified:
        await update.message.reply_text("شما قبلاً احراز هویت شده‌اید و می‌توانید در گروه فعالیت کنید.")
        session.close()
        return ConversationHandler.END
    
    if not db_user:
        db_user = User(
            user_id=user.id,
            chat_id=update.effective_chat.id,
            first_name=user.first_name,
            last_name=user.last_name or ""
        )
        session.add(db_user)
        session.commit()
    
    session.close()
    
    await update.message.reply_text(
        "سلام! به ربات احراز هویت گروه مسکن ملی پویان بتن نیشابور خوش آمدید.\n\n"
        "لطفاً نام و نام خانوادگی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return GET_NAME

async def get_name(update: Update, context: CallbackContext):
    full_name = update.message.text
    names = full_name.split(' ', 1)
    
    if len(names) < 2:
        await update.message.reply_text("لطفاً هم نام و هم نام خانوادگی خود را وارد کنید:")
        return GET_NAME
    
    context.user_data['first_name'] = names[0]
    context.user_data['last_name'] = names[1]
    
    # ایجاد دکمه اشتراک گذاری شماره تلفن
    keyboard = [[KeyboardButton("اشتراک گذاری شماره تلفن", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "لطفاً شماره تلفن خود را از طریق دکمه زیر اشتراک گذاری کنید:",
        reply_markup=reply_markup
    )
    
    return GET_PHONE

async def get_phone(update: Update, context: CallbackContext):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        context.user_data['phone_number'] = phone_number
        
        await update.message.reply_text(
            "لطفاً بخش اول اسکرین‌شات مربوط به سایت مسکن ملی را ارسال کنید:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return GET_SCREENSHOT1
    else:
        await update.message.reply_text("لطفاً از طریق دکمه اشتراک گذاری شماره تلفن اقدام کنید.")
        return GET_PHONE

async def get_screenshot1(update: Update, context: CallbackContext):
    # ذخیره فایل آیدی اسکرین‌شات اول
    photo_file = update.message.photo[-1].file_id
    context.user_data['screenshot1_file_id'] = photo_file
    
    await update.message.reply_text("لطفاً بخش دوم اسکرین‌شات مربوط به سایت مسکن ملی را ارسال کنید:")
    return GET_SCREENSHOT2

async def get_screenshot2(update: Update, context: CallbackContext):
    # ذخیره فایل آیدی اسکرین‌شات دوم
    photo_file = update.message.photo[-1].file_id
    context.user_data['screenshot2_file_id'] = photo_file
    
    # نمایش خلاصه اطلاعات برای تأیید
    summary = f"""
📋 اطلاعات وارد شده:
    
👤 نام و نام خانوادگی: {context.user_data['first_name']} {context.user_data['last_name']}
📞 شماره تلفن: {context.user_data['phone_number']}

لطفاً تأیید کنید که اطلاعات فوق صحیح است. در صورت تأیید، اطلاعات برای مدیران ارسال خواهد شد.
"""
    
    await update.message.reply_text(summary)
    await update.message.reply_text("آیا اطلاعات فوق صحیح است؟ (بله/خیر)")
    
    return CONFIRMATION

async def confirmation(update: Update, context: CallbackContext):
    response = update.message.text.lower()
    
    if response in ['بله', 'yes', 'y', 'آره']:
        # ذخیره اطلاعات کاربر در دیتابیس
        session = Session()
        user = session.query(User).filter(User.user_id == update.effective_user.id).first()
        
        if user:
            user.first_name = context.user_data['first_name']
            user.last_name = context.user_data['last_name']
            user.phone_number = context.user_data['phone_number']
            user.screenshot1_file_id = context.user_data['screenshot1_file_id']
            user.screenshot2_file_id = context.user_data['screenshot2_file_id']
            
            session.commit()
            
            # ارسال اطلاعات به ادمین‌ها
            await send_to_admins(context.bot, user)
            
            await update.message.reply_text(
                "✅ اطلاعات شما با موفقیت ثبت شد و برای تأیید به مدیران ارسال گردید.\n"
                "پس از تأیید، می‌توانید در گروه فعالیت کنید."
            )
        else:
            await update.message.reply_text("❌ خطایی در ثبت اطلاعات رخ داده است. لطفاً دوباره تلاش کنید.")
        
        session.close()
        return ConversationHandler.END
    
    elif response in ['خیر', 'no', 'n', 'نه']:
        await update.message.reply_text("لطفاً فرآیند احراز هویت را از ابتدا شروع کنید. /start")
        return ConversationHandler.END
    
    else:
        await update.message.reply_text("لطفاً پاسخ معتبر وارد کنید (بله/خیر):")
        return CONFIRMATION

async def send_to_admins(bot, user):
    message_text = f"""
📋 درخواست احراز هویت جدید:

👤 نام و نام خانوادگی: {user.first_name} {user.last_name}
📞 شماره تلفن: {user.phone_number}
🆔 آیدی کاربر: {user.user_id}
📅 تاریخ ثبت: {user.created_at}
"""
    
    for admin_id in ADMIN_IDS:
        try:
            # ارسال متن اطلاعات
            await bot.send_message(admin_id, message_text)
            
            # ارسال اسکرین‌شات‌ها
            if user.screenshot1_file_id:
                await bot.send_photo(admin_id, user.screenshot1_file_id, caption="اسکرین‌شات بخش اول")
            if user.screenshot2_file_id:
                await bot.send_photo(admin_id, user.screenshot2_file_id, caption="اسکرین‌شات بخش دوم")
                
            # ارسال دکمه‌های تأیید/رد
            # (این بخش نیاز به پیاده سازی با InlineKeyboard دارد)
            
        except Exception as e:
            print(f"Error sending message to admin {admin_id}: {e}")

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "فرآیند احراز هویت لغو شد. هر زمان که خواستید می‌توانید با ارسال /start دوباره شروع کنید.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def help_command(update: Update, context: CallbackContext):
    help_text = """
🤖 راهنمای ربات احراز هویت

🔹 برای شروع فرآیند احراز هویت: /start
🔹 برای مشاهده این راهنما: /help
🔹 برای لغو فرآیند: /cancel

📝 مراحل احراز هویت:
1. وارد کردن نام و نام خانوادگی
2. اشتراک گذاری شماره تلفن
3. ارسال بخش اول اسکرین‌شات از سایت مسکن ملی
4. ارسال بخش دوم اسکرین‌شات از سایت مسکن ملی
5. تأیید نهایی اطلاعات

📞 پشتیبانی: برای ارتباط با پشتیبانی از منوی اصلی استفاده کنید.
"""
    await update.message.reply_text(help_text)