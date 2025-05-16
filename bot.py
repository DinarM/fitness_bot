import asyncio
import logging
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.utils.markdown import html_decoration as fmt
from aiogram.utils.token import TokenValidationError
from sqlalchemy import select, update, func
from bot_dialogs import states
from db_utils.utils import get_tokens
from models import BotToken
from bot_dialogs.tests import test_dialog
from sqlalchemy import Integer, String
from db import AsyncSessionLocal
from polling_manager import PollingManager

logger = logging.getLogger(__name__)




async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="bye",
            description="test1213124'",
        ),
        BotCommand(
            command="start",
            description="test1234433'",
        ),
        BotCommand(
            command="me",
            description="Информация о пользователе",
        ),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def echo(message: types.Message):
    await message.answer(message.text)


async def bye(message: types.Message, bot: Bot):
    info = await bot.get_me()
    await message.answer(f"Command received by bot @{info} (id={bot.id})")


def setup_handlers(dp: Dispatcher, polling_manager: PollingManager, bot: Bot):
    from aiogram_dialog import DialogManager, StartMode
    from db_utils.utils import get_or_create_user
    from db import AsyncSessionLocal

    async def start_dialog_handler(message: types.Message, dialog_manager: DialogManager):
        async with AsyncSessionLocal() as session:
            await get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                telegram_bot_id=message.bot.id,
                telegram_data={
                    "username": message.from_user.username,
                    "first_name": message.from_user.first_name,
                    "last_name": message.from_user.last_name,
                }
            )
        await dialog_manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK)

    dp.message.register(start_dialog_handler, Command(commands="start"))
    dp.message.register(bye, Command(commands="bye"))

    @dp.message(Command(commands="me"))
    async def me_info_handler(message: types.Message):
        user = message.from_user
        info = (
            f"🧾 <b>Информация о пользователе</b>\n"
            f"ID: <code>{user.id}</code>\n"
            f"Username: @{user.username or 'нет'}\n"
            f"First name: {user.first_name or 'нет'}\n"
            f"Last name: {user.last_name or 'нет'}\n"
            f"Language: {user.language_code or 'не указан'}"
        )
        await message.answer(info, parse_mode="HTML")

        photos = await bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            await message.answer_photo(file_id, caption="Это твой аватар")
        else:
            await message.answer("У тебя нет аватара.")

    asyncio.create_task(set_commands(bot))

    from aiogram_dialog import setup_dialogs
    setup_dialogs(dp)


async def update_bot_info(bot: Bot, session: AsyncSessionLocal) -> bool:
    try:
        me = await bot.get_me()
        
        result = await session.execute(select(BotToken).where(BotToken.token == bot.token))
        bot_record = result.scalar_one_or_none()
        if bot_record:
            bot_record.telegram_bot_id = me.id
            bot_record.bot_username    = me.username
            await session.commit()
            logger.info(f"Информация для бота {me.username} обновлена")
            return True
        else:
            logger.warning(f"Не удалось обновить информацию для бота {me.username}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при обновлении информации бота: {str(e)}")
        await session.rollback()
        return False


# 2) В main() — создаём один Dispatcher и вешаем на него всё
async def main():
    tokens = await get_tokens()
    if not tokens:
        logger.error("No active bots found.")
        return

    polling_manager = PollingManager()
    dp = Dispatcher(events_isolation=SimpleEventIsolation())

    from bot_dialogs.main import create_main_dialog
    dp.include_routers(create_main_dialog(), test_dialog)

    # Регистрация тестового диалога
    
    # dp.include_router(test_dialog)

    bots = [Bot(token) for token in tokens]

    for bot in bots:
        try:
            await bot.get_updates(offset=-1)
            # await set_commands(bot)
            setup_handlers(dp, polling_manager, bot)
            async with AsyncSessionLocal() as session:
                polling_manager.start_bot_polling(dp=dp, bot=bot)
                await update_bot_info(bot, session)
        except Exception as e:
            logger.error(f"Ошибка при инициализации бота {bot.token[:8]}...: {str(e)}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Exit")