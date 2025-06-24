import logging
import requests
import schedule
import time
import asyncio
from datetime import datetime
from telegram.constants import ParseMode
import random
import pytz

# === Налаштування ===
TELEGRAM_TOKEN = '7913456658:AAHS0nOMwlW89gMMGyvNEvHWZm7m9HQS2hs'
WEATHER_API_KEY = '28239cd5e279eb988fc138c29ade9c93'
CHAT_ID = -4830493043

CITY_COORDS = {
    'Київ': (50.45, 30.52),
    'Варшава': (52.23, 21.01),
    'Аланія': (36.54, 32.00)
}

CITY_TZ = {
    'Київ': 'Europe/Kyiv',
    'Варшава': 'Europe/Warsaw',
    'Аланія': 'Europe/Istanbul'
}

# === Прогноз погоди ===
def get_forecast_text(city_name):
    lat, lon = CITY_COORDS[city_name]
    tz = CITY_TZ[city_name]
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ua'

    try:
        res = requests.get(url).json()

        # 🐞 DEBUG — друкуємо відповідь від API
        print(f"[DEBUG] {city_name} raw forecast: {res}")

        if "list" not in res or not res["list"]:
            return f"{city_name.ljust(9)} 🔴 немає даних від API"

        forecast_list = res['list']

        morning = get_forecast_for_period(forecast_list, tz, 6, 11)
        afternoon = get_forecast_for_period(forecast_list, tz, 12, 16)
        evening = get_forecast_for_period(forecast_list, tz, 17, 21)

        def emoji(desc):
            desc = desc.lower()
            if "дощ" in desc:
                return "🌧️"
            if "гроза" in desc:
                return "⛈️"
            if "сніг" in desc:
                return "🌨️"
            if "сонячно" in desc or "ясно" in desc:
                return "☀️"
            if "хмар" in desc:
                return "⛅"
            if "туман" in desc:
                return "🌫️"
            return "🌤️"

        def format_period(period):
            if period == "немає даних":
                return "—"
            parts = period.split(", ")
            temp = parts[0]
            desc = parts[1] if len(parts) > 1 else ""
            return f"{emoji(desc)} {temp}"

        return f"{city_name.ljust(9)} {format_period(morning)}   {format_period(afternoon)}   {format_period(evening)}"

    except Exception as e:
        print(f"[ERROR] {city_name}: {e}")
        return f"{city_name.ljust(9)} ⚠️ помилка API"


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

# === Тестовий запуск ===
async def send_digest():
    message = f"""📅 *Доброго ранку, команда!*
Ось ваш ранковий дайджест на сьогодні:

{get_weather_summary()}

♓ *Гороскоп для Риб:* {get_horoscope(ZODIACS['Риби'])}

♐ *Гороскоп для Стрільця:* {get_horoscope(ZODIACS['Стрілець'])}

📊 *Порада для бізнес-аналітика:*
{get_ba_tip()}"""

    print("=== Готовий дайджест ===")
    print(message)

if __name__ == "__main__":
    asyncio.run(send_digest())
