from sqlalchemy import select
from app.db.models import BotToken
from app.db.database import AsyncSessionLocal
from aiogram import Bot




async def get_tokens():
    """Fetch active bot tokens from the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(BotToken).where(BotToken.is_active == True))
        return [bt.token for bt in result.scalars().all()]


# async def start_dialog_handler(message: types.Message, dialog_manager: DialogManager):
#     print(f"Команда /start получена от пользователя: {message.from_user.id}")
#     await user_repository.get_or_create_user(
#         telegram_id=message.from_user.id,
#         telegram_bot_id=message.bot.id,
#         telegram_data={
#             "username": message.from_user.username,
#             "first_name": message.from_user.first_name,
#             "last_name": message.from_user.last_name,
#         }
#     )
#     await dialog_manager.start(states.Main.MAIN, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,)


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
    

