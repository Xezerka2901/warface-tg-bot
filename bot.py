import requests
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import pytz

# Ваш токен и chat_id
TOKEN = '7912815635:AAGdKqihiMsKEe8VSNBL-3OUw70iwQs7CVY'
CHAT_ID = '-1002644568185'

# Инициализация бота и планировщика
bot = Bot(token=TOKEN)
app = ApplicationBuilder().token(TOKEN).build()
scheduler = AsyncIOScheduler()

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
async def send_daily_tournaments():
    tournaments = get_warface_tournaments()
    if tournaments:
        message = "🎮 Активные турниры по Warface:\n\n"
        for t in tournaments:
            message += f"🏆 {t['title']}\n🔗 {t['url']}\n\n"
        await bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await bot.send_message(chat_id=CHAT_ID, text="Сегодня нет активных турниров по Warface.")

# Задача: оповещение за час до окончания регистрации
async def notify_before_registration_end():
    tournaments = get_warface_tournaments()
    now = datetime.now(pytz.utc)
    for t in tournaments:
        reg_end = datetime.fromisoformat(t['registration_end_time']).astimezone(pytz.utc)
        if timedelta(hours=0) < reg_end - now <= timedelta(hours=1):
            message = f"⏰ Остался 1 час до окончания регистрации на турнир:\n🏆 {t['title']}\n🔗 {t['url']}"
            await bot.send_message(chat_id=CHAT_ID, text=message)

# Планирование задач
scheduler.add_job(send_daily_tournaments, 'cron', hour=13, minute=0, timezone=moscow_tz)
scheduler.add_job(notify_before_registration_end, 'interval', minutes=30)

# Запуск бота и планировщика
async def main():
    scheduler.start()
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

import asyncio
asyncio.run(main())