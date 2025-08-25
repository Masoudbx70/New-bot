from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from models.database import User, get_db
import config.config as config

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_message = """
📞 پشتیبانی ربات مسکن ملی پویان بتن نیشابور

برای دریافت کمک و راهنمایی می‌توانید با روش‌های زیر با ما در ارتباط باشید:

📧 ایمیل: support@puyanbeton.ir
☎️ تلفن: ۰۵۱۴۲۳۴۵۶۷۸
🕘 ساعت پاسخگویی: ۹ صبح تا ۵ عصر

همچنین می‌توانید سؤالات خود را از طریق این ربات مطرح کنید و در اسرع وقت پاسخ خواهید گرفت.
"""
    
    await update.message.reply_text(support_message)

async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text
    
    # ذخیره پیام پشتیبانی در دیتابیس یا ارسال به ادمین‌ها
    support_message = f"""
📩 پیام پشتیبانی جدید از کاربر:
👤 کاربر: {update.message.from_user.first_name} {update.message.from_user.last_name or ''}
🆔 آی‌دی: {user_id}
👤 نام کاربری: @{update.message.from_user.username or 'ندارد'}

📝 متن پیام:
{message_text}
"""
    
    for admin_id in config.ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, support_message)
        except Exception as e:
            print(f"Error sending support message to admin {admin_id}: {e}")
    
    await update.message.reply_text("✅ پیام شما با موفقیت ثبت شد و در اسرع وقت پاسخ داده خواهد شد.")