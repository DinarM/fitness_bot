import asyncio
import logging
from typing import List

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.types import BotCommand, BotCommandScopeDefault, Message
from aiogram.utils.markdown import html_decoration as fmt
from aiogram.utils.token import TokenValidationError
from sqlalchemy import select, update, func
from bot_dialogs import states
from db_utils.utils import get_tokens, update_bot_info
from models import BotToken
from bot_dialogs.tests import test_dialog
from sqlalchemy import Integer, String
from db import AsyncSessionLocal
from polling_manager import PollingManager
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot_dialogs.select import selects_dialog
from bot_dialogs.main import main_dialog
from bot_dialogs.tests import test_dialog
from db_utils.utils import start_dialog_handler
from db import AsyncSessionLocal
from aiogram_dialog import setup_dialogs

logger = logging.getLogger(__name__)


dialog_router = Router()
dialog_router.include_routers(
    main_dialog,
    test_dialog,
    selects_dialog,
)


def setup_handlers(dp: Dispatcher, polling_manager: PollingManager, bot: Bot):

    dp.message.register(start_dialog_handler, Command(commands="start"))
    setup_dialogs(dp)


async def main():
    tokens = await get_tokens()

    polling_manager = PollingManager()
    dp = Dispatcher(storage=MemoryStorage(), events_isolation=SimpleEventIsolation()) 

    dp.include_router(dialog_router)

    bots = [Bot(token) for token in tokens]

    for bot in bots:
        try:
            await bot.get_updates(offset=-1)
            setup_handlers(dp, polling_manager, bot)
            async with AsyncSessionLocal() as session:
                polling_manager.start_bot_polling(dp=dp, bot=bot)
                await update_bot_info(bot, session)
        except Exception as e:
            logger.error(f"Ошибка при инициализации бота {bot.token[:8]}...: {str(e)}")

    while True:
        await asyncio.sleep(1) 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Exit")