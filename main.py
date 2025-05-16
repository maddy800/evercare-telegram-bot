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
user_lang = {}  # Optional: track user preferred language

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if update.effective_user.language_code == "fa":
        user_lang[user_id] = "fa"
        await context.bot.send_message(chat_id=user_id, text="سلام! من EverCareBot هستم 🌿 و قراره یادآوری‌های مهربون برات بفرستم.")
    else:
        user_lang[user_id] = "en"
        await context.bot.send_message(chat_id=user_id, text="Hi! I'm EverCareBot 🌿 here to send you kind reminders and warm support.")

# test reminder
async def send_test_reminder():
    await bot.send_message(chat_id=USER_ID, text="🌙 Test Reminder: EverCareBot is working!")

# /remindme command with support for date and time and repetition
async def remindme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_chat.id
        lang = user_lang.get(user_id, "fa")

        if not context.args:
            msg = "لطفاً زمان و پیام یادآوری را وارد کن.\nمثال: /remindme 10min نوشیدن آب" if lang == "fa" else "Please provide time and message.\nExample: /remindme 10min drink water"
            await update.message.reply_text(msg)
            return

        message = ' '.join(context.args)
        repeat = None
        if "daily" in message.lower():
            repeat = "daily"
            message = message.lower().replace("daily", "").strip()
        elif "weekly" in message.lower():
            repeat = "weekly"
            message = message.lower().replace("weekly", "").strip()

        match_date = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+(.*)', message)
        if match_date:
            date_str, time_str, task = match_date.groups()
            reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            delay = (reminder_time - datetime.now()).total_seconds()
            if delay <= 0:
                msg = "زمان وارد شده گذشته است." if lang == "fa" else "The time has already passed."
                await update.message.reply_text(msg)
                return
        else:
            match_short = re.match(r'(\d+)(min|h)\s+(.*)', message)
            if not match_short:
                msg = "فرمت درست: /remindme YYYY-MM-DD HH:MM پیام شما یا /remindme 10min پیام شما" if lang == "fa" else "Format: /remindme YYYY-MM-DD HH:MM message or /remindme 10min message"
                await update.message.reply_text(msg)
                return
            value, unit, task = match_short.groups()
            delay = int(value) * 60 if unit == 'min' else int(value) * 3600
            reminder_time = datetime.now() + timedelta(seconds=delay)

        reminder_tasks[user_id] = reminder_tasks.get(user_id, [])
        reminder_tasks[user_id].append((task, reminder_time))

        msg = f"یادآوری تنظیم شد برای {reminder_time.strftime('%Y-%m-%d %H:%M')} : {task}" if lang == "fa" else f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M')}: {task}"
        await update.message.reply_text(msg)

        async def send_reminder():
            await asyncio.sleep(delay)
            remind_msg = f"⏰ یادآوری: {task}" if lang == "fa" else f"⏰ Reminder: {task}"
            await context.bot.send_message(chat_id=user_id, text=remind_msg)
            if repeat == "daily":
                while True:
                    await asyncio.sleep(86400)  # 24h
                    await context.bot.send_message(chat_id=user_id, text=remind_msg)
            elif repeat == "weekly":
                while True:
                    await asyncio.sleep(604800)  # 7 days
                    await context.bot.send_message(chat_id=user_id, text=remind_msg)

        asyncio.create_task(send_reminder())

    except Exception as e:
        msg = "خطا در تنظیم یادآوری. لطفاً دوباره تلاش کن." if lang == "fa" else "Error setting reminder. Please try again."
        await update.message.reply_text(msg)

# /list command
async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    lang = user_lang.get(user_id, "fa")
    reminders = reminder_tasks.get(user_id, [])
    if not reminders:
        msg = "یادآوری فعالی وجود ندارد." if lang == "fa" else "No active reminders."
        await update.message.reply_text(msg)
        return

    reply = "📋 لیست یادآوری‌های فعال:\n" if lang == "fa" else "📋 Active Reminders:\n"
    for idx, (task, time) in enumerate(reminders, 1):
        minutes_left = int((time - datetime.now()).total_seconds() // 60)
        entry = f"{idx}. {task} (تا {time.strftime('%Y-%m-%d %H:%M')} | حدود {minutes_left} دقیقه دیگر)\n" if lang == "fa" else f"{idx}. {task} (at {time.strftime('%Y-%m-%d %H:%M')} | in ~{minutes_left} minutes)\n"
        reply += entry
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
    await app.run_polling()

# entrypoint
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())