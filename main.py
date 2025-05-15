from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os
import nest_asyncio

# Environment-safe (or hardcoded during testing)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "توکن_اینجا_بذار_برای_تست")
USER_ID = int(os.environ.get("USER_ID", "105692584"))

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

# main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

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


