from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import os
import nest_asyncio
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_ID = 105692584

bot = Bot(token=BOT_TOKEN)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """سلام! من EverCareBot هستم 🌿 و قراره یادآوری‌های مهربون برات بفرستم.
Hi! I'm EverCareBot 🌿 here to send you kind reminders and warm support."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# test reminder
async def send_test_reminder():
    await bot.send_message(chat_id=USER_ID, text="""🌙 یادآوری تستی: ربات فعال است.
🌙 Test Reminder: EverCareBot is working!""")

# /remindme command
async def remindme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = ' '.join(context.args)
        match = re.match(r'(\d+)(min|h)\s+(.*)', message)
        if not match:
            await update.message.reply_text("لطفاً فرمت درست وارد کن: /remindme 10min آب بخور")
            return

        value, unit, task = match.groups()
        delay = int(value) * 60 if unit == 'min' else int(value) * 3600

        await update.message.reply_text(f"یادآوری تنظیم شد: {task} در {value} {unit} بعد.")

        async def send_reminder():
            await asyncio.sleep(delay)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⏰ یادآوری: {task}")

        asyncio.create_task(send_reminder())

    except Exception as e:
        await update.message.reply_text("خطا در تنظیم یادآوری. لطفاً دوباره تلاش کن.")

# main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remindme", remindme))

    async def after_start():
        await asyncio.sleep(3)
        await send_test_reminder()

    app.post_init = after_start
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    while True:
        await asyncio.sleep(60)

# entrypoint
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())