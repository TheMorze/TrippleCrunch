import asyncio
import sys
import logging

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis

from app.handlers.admin import a_commands, a_messages, a_callbacks
from app.handlers.user import handlers

from config import load_config
from app.database.requests import Database


async def main() -> None:
    config = load_config()
    logging.basicConfig(
    level=logging.DEBUG,
    format='[{asctime}] #{levelname:8} {filename}:{funcName}'
           '{lineno} - {name} - {message}',
    style='{'
    )

    await Database.create_tables()

    bot = Bot(config.tg_bot.token, parse_mode='HTML')
    redis = Redis(host='localhost')
    dp = Dispatcher(redis=redis)

    # Подключаем хэндлеры админки
    dp.include_routers(
        a_commands.router,
        a_messages.router,
        a_callbacks.router
    )

    # Подключаем хэндлеры пользователей
    dp.include_routers(
        handlers.router
    )

    logger.info('Bot was successfully started!')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

