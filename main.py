
# EverCare Reminder Bot - Version 2 (python-telegram-bot compatible with Replit)
# Author: ChatGPT for Maddy

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os

# Replace with your actual bot token
BOT_TOKEN = '7711266472:AAETBtrElR81y6SL3kvqeSHQQua9htzM26M'
USER_ID = 105692584

# Create bot instance
bot = Bot(token=BOT_TOKEN)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """سلام! من EverCareBot هستم 🌿 و قراره یادآوری‌های مهربون برات بفرستم.
Hi! I'm EverCareBot 🌿 here to send you kind reminders and warm support."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# Send test message on startup
async def send_test_reminder():
    await bot.send_message(chat_id=USER_ID, text="""🌙 یادآوری تستی: ربات فعال است.
🌙 Test Reminder: EverCareBot is working!""")

# Main async function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    async def startup_task():
        await asyncio.sleep(3)  # Wait 3 seconds after bot starts
        await send_test_reminder()

    app.post_init = startup_task  # Runs after polling starts

    # Run the bot
    await app.run_polling()

# Run main
if __name__ == '__main__':
    asyncio.run(main())
