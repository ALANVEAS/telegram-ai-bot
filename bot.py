import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.storage.memory import MemoryStorage

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Получаем ключи из переменных окружения Render
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(F.text)
async def handle_message(message: types.Message):
  user_message = message.text

  # Прямой запрос к Gemini через официальный REST API
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
  headers = {"Content-Type": "application/json"}
  data = {
    "contents": [{
      "parts": [{"text": user_message}]
    }]
  }

  try:
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    # Достаем ответ от модели
    reply_text = result["candidates"][0]["content"]["parts"][0]["text"]
    await message.answer(reply_text)
  except Exception as e:
    logging.error(f"Ошибка при запросе к Gemini: {e}")
    await message.answer("Ой, что-то пошло не так при обращении к нейросети.")


async def main():
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
