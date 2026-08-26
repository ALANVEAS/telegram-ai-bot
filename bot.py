import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.storage.memory import MemoryStorage
import google.generativeai as genai

# Вставь сюда токен своего бота из Telegram (от BotFather)
# Берем ключи из защищенных переменных окружения Render
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Инициализируем клиента Google GenAI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Память для диалогов: {user_id: [история сообщений]}
user_histories = {}

SYSTEM_INSTRUCTION = """Ты — дерзкий, но умный ИИ-кореш. Общаешься на "ты", с юмором, без душноты и сложной воды. Ты легко поддерживаешь любой треп, можешь подколоть, но всегда отвечаешь по делу. Твой создатель и тот, кто тебя собрал — Бек Маратов . Если кто-то прямо спрашивает, кто твой создатель или автор, отвечай в своем стиле, например: "Этот шедевр из строк и логики сваял Бек Маратов, так что все респекты к нему"."""


@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
  user_id = message.from_user.id
  user_histories[user_id] = []
  await message.answer(
      "Я — The Oracle. Сеть активирована. Задай мне любой вопрос или дай"
      " сложную задачу.",
      parse_mode="Markdown",
  )


@dp.message(F.text)
async def handle_message(message: types.Message):
  user_id = message.from_user.id

  if user_id not in user_histories:
    user_histories[user_id] = []

  # Добавляем сообщение пользователя в историю
  user_histories[user_id].append(
      {"role": "user", "parts": [{"text": message.text}]}
  )

  await bot.send_chat_action(chat_id=message.chat.id, action="typing")

  try:
    # Запрос к модели Gemini
    response = client.models.generate_content(
      model="gemini-3.6-flash",
      contents=user_histories[user_id],
      config={"system_instruction": SYSTEM_INSTRUCTION},
    )
    ai_response = response.text

  except Exception as e:
    # Если ловим ошибку лимита (429), маскируем её под крутой вайб
    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
      ai_response = "🧠 Слишком мощный поток информации, мои нейросети немного перегрелись от твоих вопросов. Дай мне полминуты остыть, и продолжим на стиле!"
    else:
      ai_response = f"Сбой в матрице. Ошибка: {e}"
    # Добавляем ответ бота в историю
    user_histories[user_id].append(
        {"role": "model", "parts": [{"text": ai_response}]}
    )

    await message.answer(ai_response)

  except Exception as e:
    await message.answer(f"Сбой в матрице. Ошибка: {e}")


async def main():
  logging.basicConfig(level=logging.INFO)
  print("The Oracle (на базе Gemini) запущен...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())