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
from models import BotToken

from sqlalchemy import Integer, String
from db import AsyncSessionLocal
from polling_manager import PollingManager

logger = logging.getLogger(__name__)

async def get_tokens():
    """Fetch active bot tokens from the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotToken).where(BotToken.is_active == True))
        return [bt.token for bt in result.scalars().all()]

# TOKENS  = asyncio.run(get_tokens())

ADMIN_ID = 1234567890


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="add_bot",
            description="add bot, usage '/add_bot 123456789:qwertyuiopasdfgh'",
        ),
        BotCommand(
            command="stop_bot",
            description="stop bot, usage '/stop_bot 123456789'",
        ),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


# async def on_bot_startup(bot: Bot):
#     await set_commands(bot)
#     await bot.send_message(chat_id=ADMIN_ID, text="Bot started!")


# async def on_bot_shutdown(bot: Bot):
#     # await bot.send_message(chat_id=ADMIN_ID, text="Bot shutdown!")


# async def on_startup(bots: List[Bot]):
#     for bot in bots:
#         await on_bot_startup(bot)


# async def on_shutdown(bots: List[Bot]):
#     for bot in bots:
#         await on_bot_shutdown(bot)


async def add_bot(
    message: types.Message,
    command: CommandObject,
    dp_for_new_bot: Dispatcher,            # это тот же dp, что и для главного
    polling_manager: PollingManager,
):
    token = command.args.strip()
    bot = Bot(token)
    if bot.id in polling_manager.polling_tasks:
        await message.answer("Этот бот уже запущен")
        return

    # просто стартуем новую polling-задачу, используя тот же диспетчер
    polling_manager.start_bot_polling(dp=dp_for_new_bot, bot=bot)
    info = await bot.get_me()
    await message.answer(f"Бот запущен: @{info.username}")


async def stop_bot(
    message: types.Message, command: CommandObject, polling_manager: PollingManager
):
    if command.args:
        try:
            polling_manager.stop_bot_polling(int(command.args))
            await message.answer("Bot stopped")
        except (ValueError, KeyError) as err:
            await message.answer(fmt.quote(f"{type(err).__name__}: {str(err)}"))
    else:
        await message.answer("Please provide bot id")


async def echo(message: types.Message):
    await message.answer(message.text)


async def bye(message: types.Message, bot: Bot):
    info = await bot.get_me()
    await message.answer(f"Command received by bot @{info.username} (id={bot.id})")


# 1) Вынесите регистрацию хендлеров в одну функцию
def setup_handlers(dp: Dispatcher, polling_manager: PollingManager):
    dp.message.register(echo, Command(commands="start"))
    dp.message.register(bye, Command(commands="bye"))
    dp.message.register(
        lambda msg, cmd: add_bot(msg, cmd, dp, polling_manager),
        Command(commands="add_bot")
    )
    dp.message.register(
        lambda msg, cmd: stop_bot(msg, cmd, polling_manager),
        Command(commands="stop_bot")
    )
    dp.message.register(echo)  # fallback


async def update_bot_info(bot: Bot, session: AsyncSessionLocal) -> bool:
    try:
        me = await bot.get_me()
        
        # Проверяем существование записи
        # stmt = select(BotToken).where(BotToken.token == bot.token)
        # result = await session.execute(stmt)
        # bot_token = result.scalar_one_or_none()
        
        # if not bot_token:
        #     logger.error(f"Бот с токеном {bot.token[:8]}... не найден в базе")
        #     return False
            
        # Обновляем информацию
            # Fetch the BotToken record and update its attributes
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

    # регистрируем ВСЕ общие хендлеры на главном dp
    setup_handlers(dp, polling_manager)

    # создаём список инстансов ботов
    bots = [Bot(token) for token in tokens]

    # стартуем изначальные боты
    for bot in bots:
        try:
            await bot.get_updates(offset=-1)
            async with AsyncSessionLocal() as session:
                polling_manager.start_bot_polling(dp=dp, bot=bot)
                await update_bot_info(bot, session)
        except Exception as e:
            logger.error(f"Ошибка при инициализации бота {bot.token[:8]}...: {str(e)}")

    # Запускаем главный dp (он будет обслуживать add_bot/stop_bot и при этом порождать новые polling'и)
    # await dp.start_polling(*bots, skip_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Exit")