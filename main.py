import logging
import requests
import asyncio
from datetime import datetime
import random
import pytz

# === Налаштування ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def get_forecast_text(city_name):
    lat, lon = CITY_COORDS[city_name]
    tz = CITY_TZ[city_name]
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ua'

    try:
        res = requests.get(url)
        logger.info(f"[{city_name}] Raw API response: {res.status_code} {res.text}")
        data = res.json()

        if "list" not in data or not data["list"]:
            return f"{city_name.ljust(9)} 🔴 немає даних від API"

        forecast_list = data['list']

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
        logger.exception(f"[{city_name}] Exception during weather fetch")
        return f"{city_name.ljust(9)} ⚠️ помилка API"

def get_weather_summary():
    lines = [get_forecast_text(city) for city in CITY_COORDS]
    return "📅 *Прогноз погоди на сьогодні:*\n\n" + "\n".join(lines)

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
