# Telegram Daily Digest Bot

Цей бот надсилає щоденне повідомлення в Telegram-групу (пн–пт, 09:00), що включає:
- Погоду для Києва, Варшави та Аланії
- Гороскоп для Риб і Стрільця
- Пораду для бізнес-аналітика зі списку

## 🔧 Що потрібно

1. Python 3.10+
2. API ключі:
   - Telegram Bot Token (отримати у @BotFather)
   - OpenWeatherMap API Key (https://openweathermap.org/api)

## 📦 Установка

```bash
pip install -r requirements.txt
```

Заповни змінні `TELEGRAM_TOKEN` і `WEATHER_API_KEY` у `main.py`, потім запусти:

```bash
python main.py
```

## ☁ Хостинг

Для безкоштовного хостингу можна використати:
- [Render](https://render.com/)
- [Replit](https://replit.com/)
- [Railway](https://railway.app/)
