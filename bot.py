# bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN  # Оставим для теста, но не используем
from handlers.test_handler import router as test_router
from aiogram.client.bot import Bot, DefaultBotProperties
from db import get_session
from models import BotToken

async def start_bot(token: str):
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()
    dp.include_router(test_router)
    await bot.set_my_commands([
        BotCommand(command="start_test", description="Начать тест")
    ])
    logging.info(f"Бот с токеном {token[:8]}... запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def main():
    logging.basicConfig(level=logging.INFO)
    from sqlalchemy import select
    bots = []
    async for session in get_session():
        result = await session.execute(select(BotToken).where(BotToken.is_active == True))
        bots = result.scalars().all()
        break
    if not bots:
        logging.error("Нет активных ботов в базе!")
        return
    tasks = [start_bot(bot.token) for bot in bots]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())