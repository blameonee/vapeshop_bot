import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession


# Импортируем твои будущие роутеры (обработчики)
from handlers.user import user_router
from handlers.admin import admin_router
#from database import init_db

from database import init_db

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():

    # Настраиваем логирование (чтобы видеть ошибки в консоли)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )



    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    # Важно: admin_router обычно ставим выше, чтобы команды админа не перехватывались юзерскими
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Удаляем вебхуки и запускаем чистый поллинг
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logging.info("Бот для Vape Shop запущен!")
        await init_db() #Сначала обязательно идет инициализация БД
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Критическая ошибка при работе: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")