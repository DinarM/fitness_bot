from app.db.models import BotToken
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select
from aiogram import Bot

class BotRepo(BaseRepo):
    @with_session
    async def get_id_by_telegram_id(self, telegram_bot_id: int, session: Optional[AsyncSession] = None) -> int:
        """
        Получает ID бота по его telegram_id
        Args:
            telegram_bot_id: Telegram ID бота
            session: Опциональная существующая сессия
        Returns:
            int: ID бота в базе данных
        Raises:
            ValueError: Если бот не найден
        """
        bot = await self.get_by_field(session=session, telegram_bot_id=telegram_bot_id)
        if not bot:
            raise ValueError(f"BotToken not found for telegram_bot_id={telegram_bot_id}")
        return bot.id

    @with_session
    async def update_bot_info(self, bot: Bot, session: AsyncSession = None) -> bool:
        """
        Обновляет информацию о боте в БД
        Args:
            bot: Объект бота
            session: Сессия БД (опционально)
        Returns:
            bool: True если обновление успешно, False в противном случае
        """
        try:
            me = await bot.get_me()
            
            result = await session.execute(
                select(self.model).where(self.model.token == bot.token)
            )
            bot_record = result.scalar_one_or_none()
            
            if bot_record:
                bot_record.telegram_bot_id = me.id
                bot_record.bot_username = me.username
                await session.commit()
                return True
            return False
                
        except Exception:
            await session.rollback()
            return False



bot_repo = BotRepo(BotToken)