import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

from config.settings import BOT_TOKEN
from routers import commands, calendar
from routers.calendar import cmd_calendar
from utils.logger import setup_logger
from middlewares.throttling import ThrottlingMiddleware
from middlewares.user_middleware import UserMiddleware
from states.language_states import LanguageStates

async def main():
    # Настройка логирования
    setup_logger()
    logger = logging.getLogger(__name__)
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в .env файле")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация middleware
    dp.message.outer_middleware(ThrottlingMiddleware())
    dp.message.outer_middleware(UserMiddleware())
    
    # Явно регистрируем хендлер команды /calendar на уровне диспетчера, чтобы дать ему приоритет
    # Это гарантирует, что команда /calendar будет обработана cmd_calendar
    dp.message.register(cmd_calendar, Command("calendar"))
    
    # Регистрация роутеров. Хендлеры, зарегистрированные на диспетчере явно (как cmd_calendar выше),
    # имеют приоритет над хендлерами, зарегистрированными внутри роутеров.
    dp.include_router(commands.router)
    dp.include_router(calendar.router)
    
    # Запуск бота
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 