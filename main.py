import logging
import requests
import schedule
import time
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
import random
import pytz

# === Налаштування ===
TELEGRAM_TOKEN = '7913456658:AAHS0nOMwlW89gMMGyvNEvHWZm7m9HQS2hs'
WEATHER_API_KEY = '28239cd5e279eb988fc138c29ade9c93'
CHAT_ID = -4830493043

# Міста та координати
CITY_COORDS = {
    'Київ': (50.45, 30.52),
    'Варшава': (52.23, 21.01),
    'Аланія': (36.54, 32.00)
}

# Часові пояси міст
CITY_TZ = {
    'Київ': 'Europe/Kyiv',
    'Варшава': 'Europe/Warsaw',
    'Аланія': 'Europe/Istanbul'
}

bot = Bot(token=TELEGRAM_TOKEN)

# === Прогноз погоди по періодах ===
def get_forecast_for_period(forecast_list, tz_str, period_start_hour, period_end_hour):
    now = datetime.now(pytz.timezone(tz_str))
    today = now.date()
    period_entries = []

    for entry in forecast_list:
        dt = datetime.utcfromtimestamp(entry['dt']).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz_str))
        if dt.date() == today and period_start_hour <= dt.hour <= period_end_hour:
            period_entries.append(entry)

    if not period_entries:
        return "немає даних"

    avg_temp = round(sum(e['main']['temp'] for e in period_entries) / len(period_entries))
    main_desc = period_entries[0]['weather'][0]['description'].capitalize()
    return f"{avg_temp}°C, {main_desc}"

def get_weather_forecast(city_name):
    lat, lon = CITY_COORDS[city_name]
    tz = CITY_TZ[city_name]

    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ua'
    try:
        res = requests.get(url).json()
        forecast_list = res['list']

        morning = get_forecast_for_period(forecast_list, tz, 6, 11)
        afternoon = get_forecast_for_period(forecast_list, tz, 12, 16)
        evening = get_forecast_for_period(forecast_list, tz, 17, 21)

        return f"""🌤 *Погода в {city_name}:*
🕘 Ранок: {morning}
🕛 Обід: {afternoon}
🌆 Вечір: {evening}"""

    except Exception as e:
        return f"Не вдалося отримати прогноз для {city_name}: {e}"

def get_all_forecasts():
    return "\n\n".join([get_weather_forecast(city) for city in CITY_COORDS])

# === Інші блоки ===
ZODIACS = {
    'Риби': 'pisces',
    'Стрілець': 'sagittarius'
}

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

# === Основна функція надсилання ===
async def send_digest():
    if datetime.now().weekday() > 4:
        return  # тільки пн–пт

    message = f"""📅 *Доброго ранку, команда!*
Ось ваш ранковий дайджест на сьогодні:

{get_all_forecasts()}

♓ *Гороскоп для Риб:* {get_horoscope(ZODIACS['Риби'])}

♐ *Гороскоп для Стрільця:* {get_horoscope(ZODIACS['Стрілець'])}

📊 *Порада для бізнес-аналітика:*
{get_ba_tip()}"""

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)

# === Планувальник ===
schedule.every().day.at("09:00").do(lambda: asyncio.run(send_digest()))

print("✅ Бот працює. Очікує на 09:00 з понеділка по пʼятницю...")

while True:
    schedule.run_pending()
    time.sleep(60)


# Тимчасовий ручний запуск:
# asyncio.run(send_digest())
