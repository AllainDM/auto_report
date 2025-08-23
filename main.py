import asyncio
import logging
from datetime import datetime

# import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import parser_user
import list_of_masters
import create_text
import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)

logging.debug("Это отладочное сообщение")
logging.info("Это информационное сообщение")
logging.warning("Это предупреждение")
logging.error("Это ошибка")
logging.critical("Это критическая ошибка")

logger = logging.getLogger(__name__)


# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    await message.answer(f"{user_id}")
    logging.debug(user_id)
    # Авторизация
    if user_id in list_of_masters.dict_of_masters_tg_id_user_id:
        logging.debug("Пользователь авторизован.")
        await message.answer("Привет! Я бот короче.")
        await message.answer(f"{user_id}")

# Обработчик команды /start
@dp.message(Command("report"))
async def cmd_start(message: types.Message):
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    # Авторизация
    if user_id in list_of_masters.dict_of_masters_tg_id_user_id:
        logging.debug("Пользователь авторизован.")
        await message.answer("Идет подготовка отчёта...")
        master_user_id = list_of_masters.dict_of_masters_tg_id_user_id[user_id]
        master = list_of_masters.dict_of_masters_user_id_name[master_user_id]
        logging.debug(master)
        # Определим сегодняшнюю дату.
        date_now = datetime.now()
        date_now = date_now.strftime("%d.%m.%Y")
        service = await parser_user.get_service(date=date_now, master=list_of_masters.dict_of_masters_tg_id_user_id[user_id])
        # connection_athome = await parser_user.get_connections_athome(date=date_now, master=list_of_masters.dict_of_masters_tg_id_user_id[user_id])
        connection_et = await parser_user.get_connections_et(date=date_now, master=list_of_masters.dict_of_masters_tg_id_user_id[user_id])
        # logging.debug(f"connection_et {connection_et}")

        # Сделаем строку для отправки боту.
        text_to_bot = create_text.create_text_to_bot(master, service, connection_et)
        # text_to_bot = create_text.create_text_to_bot(master, service, connection_athome, connection_et)


        await message.answer(text_to_bot)

        # Так же отправим разработчику при необходимости.
        if config.is_test:
            # logging.debug(f"user_id {user_id}")
            # logging.debug(f"config.tg_user_id {config.tg_user_id}")
            # Два раза не отправляем
            if str(user_id) != config.tg_user_id:
                await bot.send_message(chat_id=config.tg_user_id, text=text_to_bot)



# Обработчик текстовых сообщений
@dp.message()
async def echo(message: types.Message):
    # Узнаем ид пользователя.
    user_id = message.from_user.id
    # Авторизация
    if user_id in list_of_masters.dict_of_masters_tg_id_user_id:
        logging.debug("Пользователь авторизован.")
        await message.answer(f"Вы сказали: {message.text}")



async def main():
    await dp.start_polling(bot, allowed_updates=[])


if __name__ == "__main__":
    asyncio.run(main())

