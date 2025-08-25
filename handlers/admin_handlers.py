from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from sqlalchemy.orm import Session
from models.database import User, get_db
import config.config as config

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # بررسی آیا کاربر ادمین است
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user or not user.is_admin:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return
    
    # نمایش پنل مدیریت
    verified_users = db.query(User).filter(User.is_verified == True).count()
    pending_users = db.query(User).filter(User.is_verified == False).count()
    total_users = db.query(User).count()
    
    message_text = f"""
🛠 پنل مدیریت ربات مسکن ملی پویان بتن نیشابور

📊 آمار کاربران:
✅ کاربران تأیید شده: {verified_users}
⏳ کاربران در انتظار تأیید: {pending_users}
👥 کل کاربران: {total_users}

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
"""
    
    keyboard = [
        [{"text": "📋 لیست کاربران تأیید شده", "callback_data": "verified_list"}],
        [{"text": "📋 لیست کاربران در انتظار", "callback_data": "pending_list"}],
        [{"text": "🖼 مدیریت تصاویر راهنما", "callback_data": "manage_guide_images"}],
        [{"text": "📞 پشتیبانی", "callback_data": "support"}]
    ]
    
    await update.message.reply_text(
        message_text,
        reply_markup={"inline_keyboard": keyboard}
    )

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # بررسی آیا کاربر ادمین است
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user or not user.is_admin:
        await query.edit_message_text("شما دسترسی به این بخش را ندارید.")
        return
    
    if data == "verified_list":
        await show_verified_users(query, context)
    elif data == "pending_list":
        await show_pending_users(query, context)
    elif data == "manage_guide_images":
        await manage_guide_images(query, context)
    elif data == "support":
        await show_support_options(query, context)
    elif data.startswith("verify_"):
        user_id_to_verify = int(data.split("_")[1])
        await verify_user(query, context, user_id_to_verify)
    elif data.startswith("reject_"):
        user_id_to_reject = int(data.split("_")[1])
        await reject_user(query, context, user_id_to_reject)

async def show_verified_users(query, context):
    db = next(get_db())
    verified_users = db.query(User).filter(User.is_verified == True).all()
    
    if not verified_users:
        await query.edit_message_text("هیچ کاربر تأیید شده‌ای وجود ندارد.")
        return
    
    message_text = "✅ کاربران تأیید شده:\n\n"
    for i, user in enumerate(verified_users, 1):
        message_text += f"{i}. {user.first_name} {user.last_name or ''} - @{user.username or 'ندارد'} - {user.phone or 'ندارد'}\n"
    
    # اگر لیست خیلی طولانی است، آن را به چند پیام تقسیم کنید
    if len(message_text) > 4000:
        parts = [message_text[i:i+4000] for i in range(0, len(message_text), 4000)]
        for part in parts:
            await context.bot.send_message(query.message.chat_id, part)
        await query.edit_message_text("لیست کاربران تأیید شده ارسال شد.")
    else:
        await query.edit_message_text(message_text)

async def show_pending_users(query, context):
    db = next(get_db())
    pending_users = db.query(User).filter(User.is_verified == False).all()
    
    if not pending_users:
        await query.edit_message_text("هیچ کاربری در انتظار تأیید نیست.")
        return
    
    message_text = "⏳ کاربران در انتظار تأیید:\n\n"
    for i, user in enumerate(pending_users, 1):
        message_text += f"{i}. {user.first_name} {user.last_name or ''} - @{user.username or 'ندارد'} - {user.phone or 'ندارد'}\n"
    
    # اگر لیست خیلی طولانی است، آن را به چند پیام تقسیم کنید
    if len(message_text) > 4000:
        parts = [message_text[i:i+4000] for i in range(0, len(message_text), 4000)]
        for part in parts:
            await context.bot.send_message(query.message.chat_id, part)
        await query.edit_message_text("لیست کاربران در انتظار تأیید ارسال شد.")
    else:
        await query.edit_message_text(message_text)

async def manage_guide_images(query, context):
    message_text = """
🖼 مدیریت تصاویر راهنما

در این بخش می‌توانید تصاویر راهنمای احراز هویت را مدیریت کنید.
"""
    
    keyboard = [
        [{"text": "➕ افزودن تصویر جدید", "callback_data": "add_guide_image"}],
        [{"text": "✏️ ویرایش تصاویر موجود", "callback_data": "edit_guide_images"}],
        [{"text": "🗑 حذف تصاویر", "callback_data": "delete_guide_images"}],
        [{"text": "🔙 بازگشت به پنل مدیریت", "callback_data": "back_to_admin"}]
    ]
    
    await query.edit_message_text(
        message_text,
        reply_markup={"inline_keyboard": keyboard}
    )

async def verify_user(query, context, user_id_to_verify):
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id_to_verify).first()
    
    if user:
        user.is_verified = True
        db.commit()
        
        # ارسال پیام تبریک به کاربر
        try:
            await context.bot.send_message(
                user_id_to_verify,
                "✅ احراز هویت شما تأیید شد! اکنون می‌توانید در گروه فعالیت کنید.\n\n"
                "از بابت مسدودیت موقت پیش‌آمده پوزش می‌خواهیم."
            )
        except Exception as e:
            print(f"Error sending message to user: {e}")
        
        # ارسال پیام خوش‌آمدگویی به گروه
        try:
            await context.bot.send_message(
                config.GROUP_ID,
                f"👋 کاربر عزیز {user.first_name} {user.last_name or ''} به گروه خوش آمد!\n"
                "احراز هویت شما تأیید شد و اکنون می‌توانید در گروه فعالیت کنید."
            )
        except Exception as e:
            print(f"Error sending message to group: {e}")
        
        await query.edit_message_text("کاربر با موفقیت تأیید شد و به گروه اضافه گردید.")
    else:
        await query.edit_message_text("خطا: کاربر یافت نشد.")

async def reject_user(query, context, user_id_to_reject):
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id_to_reject).first()
    
    if user:
        # ارسال پیام رد درخواست به کاربر
        try:
            await context.bot.send_message(
                user_id_to_reject,
                "❌ متأسفیم، درخواست احراز هویت شما رد شد.\n\n"
                "لطفاً در صورت نیاز با پشتیبانی تماس بگیرید."
            )
        except Exception as e:
            print(f"Error sending message to user: {e}")
        
        # حذف کاربر از دیتابیس
        db.delete(user)
        db.commit()
        
        await query.edit_message_text("درخواست کاربر رد شد و از سیستم حذف گردید.")
    else:
        await query.edit_message_text("خطا: کاربر یافت نشد.")

async def show_support_options(query, context):
    message_text = """
📞 پشتیبانی

در این بخش می‌توانید پیام‌های پشتیبانی کاربران را مشاهده و مدیریت کنید.
"""
    
    keyboard = [
        [{"text": "📩 مشاهده پیام‌های پشتیبانی", "callback_data": "view_support_messages"}],
        [{"text": "🔙 بازگشت به پنل مدیریت", "callback_data": "back_to_admin"}]
    ]
    
    await query.edit_message_text(
        message_text,
        reply_markup={"inline_keyboard": keyboard}
    )