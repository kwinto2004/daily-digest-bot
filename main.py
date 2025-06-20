import requests
import schedule
import time
from telegram import Bot
from datetime import datetime
import random

# === Налаштування ===
TELEGRAM_TOKEN = 'ВСТАВ_СВІЙ_ТЕЛЕГРАМ_ТОКЕН'
CHAT_ID = -4830493043
WEATHER_API_KEY = 'ВСТАВ_СВІЙ_КЛЮЧ_ПОГОДИ'

CITIES = ['Kyiv', 'Warsaw', 'Alanya']
ZODIACS = {
    'Риби': 'pisces',
    'Стрілець': 'sagittarius'
}

bot = Bot(token=TELEGRAM_TOKEN)

def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua'
    res = requests.get(url).json()
    try:
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description']
        return f"- {city}: {temp}°C, {desc.capitalize()}"
    except:
        return f"- {city}: [помилка отримання погоди]"

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

def send_digest():
    if datetime.now().weekday() > 4:
        return  # лиш пн-пт
    message = (
        "📅 *Доброго ранку, команда!*
Ось ваш ранковий дайджест на сьогодні:

"
        "🌤 *Погода:*
" + get_all_weather() + "

" +
        "♓ *Гороскоп для Риб:* " + get_horoscope(ZODIACS['Риби']) + "

" +
        "♐ *Гороскоп для Стрільця:* " + get_horoscope(ZODIACS['Стрілець']) + "

" +
        "📊 *Порада для бізнес-аналітика:*
" + get_ba_tip()
    )
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

schedule.every().day.at("09:00").do(send_digest)

print("✅ Бот працює. Очікує на 09:00 з понеділка по пʼятницю...")
while True:
    schedule.run_pending()
    time.sleep(60)
