from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os
import nest_asyncio
import re
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
import uvicorn

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_ID = 105692584

bot = Bot(token=BOT_TOKEN)
reminder_tasks = {}
user_lang = {}

app_api = FastAPI()

@app_api.post("/api/reminder")
async def api_reminder(request: Request):
    data = await request.json()
    user_id = int(data.get("user_id", USER_ID))
    message = data.get("message", "10min drink water")
    lang = data.get("lang", "en")

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
            return {"status": "error", "msg": "Time already passed."}
    else:
        match_short = re.match(r'(\d+)(min|h)\s+(.*)', message)
        if not match_short:
            return {"status": "error", "msg": "Invalid format"}
        value, unit, task = match_short.groups()
        delay = int(value) * 60 if unit == 'min' else int(value) * 3600
        reminder_time = datetime.now() + timedelta(seconds=delay)

    reminder_tasks[user_id] = reminder_tasks.get(user_id, [])
    reminder_tasks[user_id].append((task, reminder_time))

    async def send_reminder():
        await asyncio.sleep(delay)
        remind_msg = f"⏰ یادآوری: {task}" if lang == "fa" else f"⏰ Reminder: {task}"
        await bot.send_message(chat_id=user_id, text=remind_msg)
        if repeat == "daily":
            while True:
                await asyncio.sleep(86400)
                await bot.send_message(chat_id=user_id, text=remind_msg)
        elif repeat == "weekly":
            while True:
                await asyncio.sleep(604800)
                await bot.send_message(chat_id=user_id, text=remind_msg)

    asyncio.create_task(send_reminder())
    return {"status": "ok", "msg": "Reminder scheduled"}

# Keep the Telegram bot logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if update.effective_user.language_code == "fa":
        user_lang[user_id] = "fa"
        await context.bot.send_message(chat_id=user_id, text="سلام! من EverCareBot هستم 🌿 و قراره یادآوری‌های مهربون برات بفرستم.")
    else:
        user_lang[user_id] = "en"
        await context.bot.send_message(chat_id=user_id, text="Hi! I'm EverCareBot 🌿 here to send you kind reminders and warm support.")

async def send_test_reminder():
    await bot.send_message(chat_id=USER_ID, text="🌙 Test Reminder: EverCareBot is working!")

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

async def remindme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = Request(scope=None)
    request._body = {"user_id": update.effective_chat.id, "message": ' '.join(context.args), "lang": user_lang.get(update.effective_chat.id, "fa")}
    await api_reminder(request)

async def startup():
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("remindme", remindme))
    bot_app.add_handler(CommandHandler("list", list_reminders))
    await bot_app.initialize()
    await bot_app.start()
    await send_test_reminder()

app_api.add_event_handler("startup", startup)

if __name__ == '__main__':
    nest_asyncio.apply()
    uvicorn.run(app_api, host="0.0.0.0", port=8000)
