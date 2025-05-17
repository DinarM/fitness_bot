from sqlalchemy import select, update, func
from models import User, TestType, TestQuestion, TestUserAnswer, BotToken, user_bots
from db import AsyncSessionLocal
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram_dialog import DialogManager, StartMode, ShowMode
from bot_dialogs import states

async def get_bot_id_by_telegram_id(session, telegram_bot_id: int) -> int:
    bot_stmt = select(BotToken).where(BotToken.telegram_bot_id == telegram_bot_id)
    bot_result = await session.execute(bot_stmt)
    bot_token = bot_result.scalar_one_or_none()
    if not bot_token:
        raise ValueError("Bot with given telegram_bot_id not found")
    return bot_token.id


async def get_or_create_user(session, telegram_id: int, telegram_bot_id: int, telegram_data: dict) -> User:
    bot_id = await get_bot_id_by_telegram_id(session, telegram_bot_id)

    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            telegram_username=telegram_data.get("username"),
            name=telegram_data.get("first_name"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    link_stmt = select(user_bots).where(user_bots.c.user_id == user.id, user_bots.c.bot_id == bot_id)
    link = (await session.execute(link_stmt)).first()
    if not link:
        await session.execute(user_bots.insert().values(user_id=user.id, bot_id=bot_id))
        await session.commit()

    return user


async def get_tokens():
    """Fetch active bot tokens from the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotToken).where(BotToken.is_active == True))
        return [bt.token for bt in result.scalars().all()]


async def start_dialog_handler(message: types.Message, dialog_manager: DialogManager):
    print(f"Команда /start получена от пользователя: {message.from_user.id}")
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
    await dialog_manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,)


async def update_bot_info(bot: Bot, session: AsyncSessionLocal) -> bool:
    try:
        me = await bot.get_me()
        
        result = await session.execute(select(BotToken).where(BotToken.token == bot.token))
        bot_record = result.scalar_one_or_none()
        if bot_record:
            bot_record.telegram_bot_id = me.id
            bot_record.bot_username    = me.username
            await session.commit()
            # logger.info(f"Информация для бота {me.username} обновлена")
            return True
        else:
            # logger.warning(f"Не удалось обновить информацию для бота {me.username}")
            return False
            
    except Exception as e:
        # logger.error(f"Ошибка при обновлении информации бота: {str(e)}")
        await session.rollback()
        return False