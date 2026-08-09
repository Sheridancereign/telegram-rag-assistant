import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers import document, question, start
from app.bot.middlewares.db_session import DbSessionMiddleware
from app.config import settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(document.router)
    dp.include_router(question.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())