import requests
from telegram.ext import ApplicationBuilder, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import pytz

TOKEN = '7912815635:AAGdKqihiMsKEe8VSNBL-3OUw70iwQs7CVY'
CHAT_ID = '-1002644568185'

# Часовой пояс МСК
moscow_tz = pytz.timezone('Europe/Moscow')

# Функция для получения списка турниров
def get_warface_tournaments():
    url = 'https://pvp.vkplay.ru/api/tournaments?game=warface&status=active'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

# Задача: отправка списка турниров в 13:00 МСК
async def send_daily_tournaments(context: ContextTypes.DEFAULT_TYPE):
    tournaments = get_warface_tournaments()
    if tournaments:
        message = "🎮 Активные турниры по Warface:\n\n"
        for t in tournaments:
            message += f"🏆 {t['title']}\n🔗 {t['url']}\n\n"
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text="Сегодня нет активных турниров по Warface.")

# Задача: оповещение за час до окончания регистрации
async def notify_before_registration_end(context: ContextTypes.DEFAULT_TYPE):
    tournaments = get_warface_tournaments()
    now = datetime.now(pytz.utc)
    for t in tournaments:
        reg_end = datetime.fromisoformat(t['registration_end_time']).astimezone(pytz.utc)
        if timedelta(hours=0) < reg_end - now <= timedelta(hours=1):
            message = f"⏰ Остался 1 час до окончания регистрации на турнир:\n🏆 {t['title']}\n🔗 {t['url']}"
            await context.bot.send_message(chat_id=CHAT_ID, text=message)

# Главная функция
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    scheduler = AsyncIOScheduler(timezone=moscow_tz)
    scheduler.add_job(send_daily_tournaments, 'cron', hour=13, minute=0, args=[ContextTypes.DEFAULT_TYPE])
    scheduler.add_job(notify_before_registration_end, 'interval', minutes=30, args=[ContextTypes.DEFAULT_TYPE])
    scheduler.start()

    await app.initialize()
    await app.start()
    print("Бот запущен.")
    await app.updater.start_polling()
    await app.updater.wait_until_shutdown()

import asyncio
asyncio.run(main())
