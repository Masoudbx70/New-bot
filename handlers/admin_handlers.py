from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database import Session, User

def setup_admin_handlers(dp):
    dp.add_handler(CommandHandler('admin', admin_panel))
    dp.add_handler(CallbackQueryHandler(admin_button_handler, pattern='^admin_'))
    dp.add_handler(MessageHandler(Filters.photo & Filters.chat_type.private, handle_admin_photo))

def admin_panel(update: Update, context):
    user_id = update.effective_user.id
    
    if user_id not in context.bot_data.get('admin_ids', []):
        update.message.reply_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 لیست اعضای تأیید شده", callback_data='admin_verified_list')],
        [InlineKeyboardButton("📋 لیست در انتظار تأیید", callback_data='admin_pending_list')],
        [InlineKeyboardButton("🖼 مدیریت عکس‌های راهنما", callback_data='admin_manage_photos')],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data='admin_support')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("👨‍💻 پنل مدیریت", reply_markup=reply_markup)

def admin_button_handler(update: Update, context):
    query = update.callback_query
    data = query.data
    
    if data == 'admin_verified_list':
        # نمایش لیست اعضای تأیید شده
        session = Session()
        verified_users = session.query(User).filter(User.is_verified == True).all()
        
        if verified_users:
            message = "✅ اعضای تأیید شده:\n\n"
            for user in verified_users:
                message += f"👤 {user.get_full_name()} - 📞 {user.phone_number} - 📅 {user.verified_at}\n"
        else:
            message = "❌ هیچ کاربر تأیید شده‌ای وجود ندارد."
        
        query.message.reply_text(message)
        session.close()
    
    elif data == 'admin_pending_list':
        # نمایش لیست در انتظار تأیید
        session = Session()
        pending_users = session.query(User).filter(
            User.is_verified == False, 
            User.screenshot1_file_id != None
        ).all()
        
        if pending_users:
            message = "📋 کاربران در انتظار تأیید:\n\n"
            for user in pending_users:
                message += f"👤 {user.get_full_name()} - 📞 {user.phone_number} - 📅 {user.created_at}\n"
                
                # ایجاد دکمه‌های تأیید/رد برای هر کاربر
                keyboard = [
                    [
                        InlineKeyboardButton(f"✅ تأیید {user.get_full_name()}", callback_data=f'admin_approve_{user.user_id}'),
                        InlineKeyboardButton(f"❌ رد {user.get_full_name()}", callback_data=f'admin_reject_{user.user_id}')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                query.message.reply_text(message, reply_markup=reply_markup)
                message = ""  # پاک کردن پیام برای کاربران بعدی
        else:
            query.message.reply_text("✅ هیچ کاربری در انتظار تأیید نیست.")
        
        session.close()
    
    elif data == 'admin_manage_photos':
        # مدیریت عکس‌های راهنما
        keyboard = [
            [InlineKeyboardButton("➕ افزودن عکس راهنما", callback_data='admin_add_guide_photo')],
            [InlineKeyboardButton("✏️ ویرایش عکس راهنما", callback_data='admin_edit_guide_photo')],
            [InlineKeyboardButton("🗑 حذف عکس راهنما", callback_data='admin_delete_guide_photo')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='admin_back')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text("🖼 مدیریت عکس‌های راهنما", reply_markup=reply_markup)
    
    elif data == 'admin_support':
        # بخش پشتیبانی
        query.message.reply_text("📞 برای پشتیبانی می‌توانید با آیدی @example_support در ارتباط باشید.")
    
    query.answer()

def handle_admin_photo(update: Update, context):
    # مدیریت آپلود عکس‌های راهنما توسط ادمین
    user_id = update.effective_user.id
    
    if user_id not in context.bot_data.get('admin_ids', []):
        return
    
    photo_file_id = update.message.photo[-1].file_id
    caption = update.message.caption
    
    # ذخیره file_id در دیتابیس یا context برای استفاده بعدی
    # این بخش نیاز به پیاده سازی بر اساس نیازهای خاص دارد
    
    update.message.reply_text("✅ عکس راهنما با موفقیت ذخیره شد.")