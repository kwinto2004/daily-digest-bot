import logging
import requests
import asyncio
from datetime import datetime
import random
import pytz
from telegram import Bot
from bs4 import BeautifulSoup

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

# === Погода ===
def get_closest_forecast(forecast_list, tz_str, target_hour):
    now = datetime.now(pytz.timezone(tz_str))
    closest_entry = None
    min_diff = float('inf')

    for entry in forecast_list:
        dt = datetime.utcfromtimestamp(entry['dt']).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz_str))
        diff = abs((dt.hour - target_hour) + (dt.date() - now.date()).days * 24)
        if diff < min_diff:
            min_diff = diff
            closest_entry = entry

    if closest_entry:
        temp = round(closest_entry['main']['temp'])
        desc = closest_entry['weather'][0]['description'].capitalize()
        return f"{temp}°C, {desc}"
    else:
        return "немає даних"

def get_forecast_text(city_name):
    lat, lon = CITY_COORDS[city_name]
    tz = CITY_TZ[city_name]
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ua'

    try:
        res = requests.get(url)
        data = res.json()

        if "list" not in data or not data["list"]:
            return f"{city_name.ljust(9)} 🔴 немає даних від API"

        forecast_list = data['list']
        morning = get_closest_forecast(forecast_list, tz, 9)
        afternoon = get_closest_forecast(forecast_list, tz, 14)
        evening = get_closest_forecast(forecast_list, tz, 19)

        def emoji(desc):
            desc = desc.lower()
            if "дощ" in desc: return "🌧️"
            if "гроза" in desc: return "⛈️"
            if "сніг" in desc: return "🌨️"
            if "сонячно" in desc or "ясно" in desc: return "☀️"
            if "хмар" in desc: return "⛅"
            if "туман" in desc: return "🌫️"
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

# === Гороскопи та поради ===
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

# === Курс валют із Мінфін ===
def get_black_market_rates_text():
    try:
        url = "https://minfin.com.ua/ua/currency/"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        block = soup.find("div", class_="sc-1x32wa2-9")
        if not block:
            return "❌ Курси валют недоступні."

        items = block.find_all("div", recursive=False)
        text = "💱 *Чорний ринок валют (Мінфін):*\n"
        for item in items:
            rows = item.find_all("div")
            if len(rows) >= 3:
                currency = rows[0].get_text(strip=True)
                buy = rows[1].get_text(strip=True)
                sell = rows[2].get_text(strip=True)
                text += f"{currency}: купівля {buy}, продаж {sell}\n"

        return text.strip()
    except Exception as e:
        logger.exception("Помилка при парсингу курсу валют")
        return "❌ Курси валют недоступні."

# === Основний дайджест ===
async def send_digest():
    bot = Bot(token=TELEGRAM_TOKEN)

    message = f"""📅 *Доброго ранку, команда!*
Ось ваш ранковий дайджест на сьогодні:

{get_weather_summary()}

{get_black_market_rates_text()}

♓ *Гороскоп для Риб:* {get_horoscope(ZODIACS['Риби'])}

♐ *Гороскоп для Стрільця:* {get_horoscope(ZODIACS['Стрілець'])}

📊 *Порада для бізнес-аналітика:*
{get_ba_tip()}"""

    print("=== Готовий дайджест ===")
    print(message)

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

if __name__ == "__main__":
    asyncio.run(send_digest())
