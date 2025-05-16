from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import os
import nest_asyncio
import re
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_ID = 105692584

bot = Bot(token=BOT_TOKEN)
reminder_tasks = {}  # Dictionary to track active reminders

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """سلام! من EverCareBot هستم 🌿 و قراره یادآوری‌های مهربون برات بفرستم.
Hi! I'm EverCareBot 🌿 here to send you kind reminders and warm support."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# test reminder
async def send_test_reminder():
    await bot.send_message(chat_id=USER_ID, text="""🌙 یادآوری تستی: ربات فعال است.
🌙 Test Reminder: EverCareBot is working!""")

# /remindme command with support for date and time
async def remindme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = ' '.join(context.args)
        user_id = update.effective_chat.id

        # Support for formats like: 2025-05-20 14:30 دارو
        match_date = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+(.*)', message)
        if match_date:
            date_str, time_str, task = match_date.groups()
            reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            delay = (reminder_time - datetime.now()).total_seconds()
            if delay <= 0:
                await update.message.reply_text("زمان وارد شده گذشته است.")
                return
        else:
            # Fallback to short format like 10min or 2h
            match_short = re.match(r'(\d+)(min|h)\s+(.*)', message)
            if not match_short:
                await update.message.reply_text("فرمت درست: /remindme YYYY-MM-DD HH:MM پیام شما یا /remindme 10min پیام شما")
                return
            value, unit, task = match_short.groups()
            delay = int(value) * 60 if unit == 'min' else int(value) * 3600
            reminder_time = datetime.now() + timedelta(seconds=delay)

        reminder_tasks[user_id] = reminder_tasks.get(user_id, [])
        reminder_tasks[user_id].append((task, reminder_time))

        await update.message.reply_text(f"یادآوری تنظیم شد برای {reminder_time.strftime('%Y-%m-%d %H:%M')} : {task}")

        async def send_reminder():
            await asyncio.sleep(delay)
            await context.bot.send_message(chat_id=user_id, text=f"⏰ یادآوری: {task}")

        asyncio.create_task(send_reminder())

    except Exception as e:
        await update.message.reply_text("خطا در تنظیم یادآوری. لطفاً دوباره تلاش کن.")

# /list command
async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    reminders = reminder_tasks.get(user_id, [])
    if not reminders:
        await update.message.reply_text("یادآوری فعالی وجود ندارد.")
        return

    reply = "📋 لیست یادآوری‌های فعال:\n"
    for idx, (task, time) in enumerate(reminders, 1):
        minutes_left = int((time - datetime.now()).total_seconds() // 60)
        reply += f"{idx}. {task} (تا {time.strftime('%Y-%m-%d %H:%M')} | حدود {minutes_left} دقیقه دیگر)\n"
    await update.message.reply_text(reply)

# main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remindme", remindme))
    app.add_handler(CommandHandler("list", list_reminders))

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