import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import asyncio

TOKEN = '7912815635:AAGdKqihiMsKEe8VSNBL-3OUw70iwQs7CVY'
CHAT_ID = '-1002644568185'
moscow_tz = pytz.timezone('Europe/Moscow')


def get_warface_tournaments():
    url = 'https://pvp.vkplay.ru/api/tournaments?game=warface&status=active'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при получении турниров: {e}")
        return []


async def send_daily_tournaments(context: ContextTypes.DEFAULT_TYPE):
    tournaments = get_warface_tournaments()
    if tournaments:
        message = "🎮 Активные турниры по Warface:\n\n"
        for t in tournaments:
            message += f"🏆 {t['title']}\n🔗 {t['url']}\n\n"
    else:
        message = "Сегодня нет активных турниров по Warface."
    await context.bot.send_message(chat_id=CHAT_ID, text=message)


async def notify_before_registration_end(context: ContextTypes.DEFAULT_TYPE):
    tournaments = get_warface_tournaments()
    now = datetime.now(pytz.utc)
    for t in tournaments:
        try:
            reg_end = parser.isoparse(t['registration_end_time']).astimezone(pytz.utc)
            if timedelta(hours=0) < reg_end - now <= timedelta(hours=1):
                message = f"⏰ Остался 1 час до окончания регистрации:\n🏆 {t['title']}\n🔗 {t['url']}"
                await context.bot.send_message(chat_id=CHAT_ID, text=message)
        except Exception as e:
            print(f"Ошибка парсинга даты: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот Warface. Жду новых турниров 😉")
    # И сразу отправим текущие турниры
    tournaments = get_warface_tournaments()
    if tournaments:
        message = "🎮 Активные турниры по Warface:\n\n"
        for t in tournaments:
            message += f"🏆 {t['title']}\n🔗 {t['url']}\n\n"
    else:
        message = "Сегодня нет активных турниров по Warface."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Команда /start
    app.add_handler(CommandHandler("start", start_command))

    # Планировщик
    scheduler = AsyncIOScheduler(timezone=moscow_tz)
    scheduler.add_job(send_daily_tournaments, 'cron', hour=13, minute=0)
    scheduler.add_job(notify_before_registration_end, 'interval', minutes=30)
    scheduler.start()

    print("Бот запущен.")
    await send_daily_tournaments(ContextTypes.DEFAULT_TYPE(bot=app.bot, job=None))  # Отправить турниры при запуске
    await app.run_polling()

asyncio.run(main())