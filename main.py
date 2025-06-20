import logging
import requests
import schedule
import time
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
import random

# === Налаштування ===
TELEGRAM_TOKEN = '7913456658:AAHS0nOMwlW89gMMGyvNEvHWZm7m9HQS2hs'
CHAT_ID = -4830493043
WEATHER_API_KEY = '28239cd5e279eb988fc138c29ade9c93'

CITIES = ['Kyiv', 'Warsaw', 'Alanya']
ZODIACS = {
    'Риби': 'pisces',
    'Стрілець': 'sagittarius'
}

bot = Bot(token=TELEGRAM_TOKEN)

def get_weather(city):
    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua'
        res = requests.get(url).json()
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description']
        return f"- {city}: {temp}°C, {desc.capitalize()}"
    except Exception as e:
        return f"- {city}: [помилка: {e}]"

def get_all_weather():
    return "\n".join([get_weather(city) for city in CITIES])

def get_horoscope(sign):
    try:
        url = f"https://ohmanda.com/api/horoscope/{sign}/"
        res = requests.get(url).json()
        return res['horoscope']
    except:
        return "Гороскоп тимчасово недоступний."

def get_ba_tip():
    try:
        with open("ba_tips.txt", encoding="utf-8") as f:
            tips = f.readlines()
        return random.choice(tips).strip()
    except:
        return "Сьогодні важливо залишатися сфокусованим 😉"

async def send_digest():
    if datetime.now().weekday() > 4:
        return  # тільки пн-пт

    message = f"""📅 *Доброго ранку, команда!*
Ось ваш ранковий дайджест на сьогодні:

🌤 *Погода:*
{get_all_weather()}

♓ *Гороскоп для Риб:* {get_horoscope(ZODIACS['Риби'])}

♐ *Гороскоп для Стрільця:* {get_horoscope(ZODIACS['Стрілець'])}

📊 *Порада для бізнес-аналітика:*
{get_ba_tip()}"""

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)

# Обгортка для запуску async функції у schedule
def scheduled_task():
    asyncio.run(send_digest())

# Запланувати о 09:00
schedule.every().day.at("09:00").do(scheduled_task)

print("✅ Бот працює. Очікує на 09:00 з понеділка по пʼятницю...")

while True:
    schedule.run_pending()
    time.sleep(60)
