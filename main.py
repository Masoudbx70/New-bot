import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.config import BOT_TOKEN, ADMIN_IDS
from handlers import group_handlers, auth_handlers, admin_handlers, support_handlers

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    # ایجاد برنامه
    application = Application.builder().token(BOT_TOKEN).build()
    
    # افزودن هندلرهای گروه
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_handlers.welcome_new_member))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_handlers.goodbye_member))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_handlers.handle_group_message))
    
    # افزودن هندلرهای احراز هویت
    application.add_handler(CommandHandler("start", auth_handlers.start))
    application.add_handler(CommandHandler("verify", auth_handlers.start_verification))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, auth_handlers.handle_verification))
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, auth_handlers.handle_screenshot))
    
    # افزودن هندلرهای مدیریت
    application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
    application.add_handler(CommandHandler("members_list", admin_handlers.members_list))
    
    # افزودن هندلرهای پشتیبانی
    application.add_handler(CommandHandler("help", support_handlers.help_command))
    application.add_handler(CommandHandler("support", support_handlers.support))
    
    # شروع ربات - برای Fly.io از webhook استفاده می‌کنیم
    if os.environ.get('FLY_APP_NAME'):
        # اجرا در Fly.io با webhook
        url = f"https://{os.environ['FLY_APP_NAME']}.fly.dev/{BOT_TOKEN}"
        await application.bot.set_webhook(url)
        logger.info(f"Webhook set to: {url}")
        
        # اجرای سرور HTTP برای Fly.io
        from aiohttp import web
        async def handle(request):
            return web.Response(text="Bot is running")
        
        app = web.Application()
        app.router.add_get('/', handle)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        logger.info("HTTP server started on port 8080")
        
        # نگه داشتن برنامه در حال اجرا
        while True:
            await asyncio.sleep(3600)
    else:
        # اجرا به صورت محلی با polling
        logger.info("Starting polling locally")
        await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
