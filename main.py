import asyncio
from datetime import datetime

# import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import parser_user
import list_of_masters
import create_text
import config

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    # Авторизация
    if user_id in config.users:
        print("Пользователь авторизован.")
        await message.answer("Привет! Я бот короче.")

# Обработчик команды /start
@dp.message(Command("report"))
async def cmd_start(message: types.Message):
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    # Авторизация
    if user_id in config.users:
        print("Пользователь авторизован.")
        # Определим сегодняшнюю дату.
        date_now = datetime.now()
        date_now = date_now.strftime("%d.%m.%Y")
        tasks = await parser_user.get_service(date=date_now, master=list_of_masters.dict_of_masters_tg_id[user_id])

        text_to_bot = create_text.create_text_to_bot(tasks)


        await message.answer(text_to_bot)


# Обработчик текстовых сообщений
@dp.message()
async def echo(message: types.Message):
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    # Авторизация
    if user_id in config.users:
        print("Пользователь авторизован.")
        await message.answer(f"Вы сказали: {message.text}")



async def main():
    await dp.start_polling(bot)

    # tasks = await parser_user.get_html(date="23.02.2025", master=234)
    # print(tasks)
    # text_to_bot = create_text.create_text_to_bot(tasks)
    #
    # tasks = await parser_user.get_html(date="23.02.2025", master=569)
    # print(tasks)
    # text_to_bot = create_text.create_text_to_bot(tasks)




if __name__ == "__main__":
    # main()
    asyncio.run(main())

