from sqlalchemy import select
from app.db.models import User, user_bots
from app.repo import bot
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

class UserRepo(BaseRepo):
    @with_session
    async def get_or_create_user(
        self, 
        telegram_id: int, 
        telegram_bot_id: int, 
        telegram_data: dict,
        session: Optional[AsyncSession] = None
    ) -> User:
        """
        Получает или создает пользователя
        Args:
            telegram_id: Telegram ID пользователя
            telegram_bot_id: Telegram ID бота
            telegram_data: Данные пользователя из Telegram
            session: Опциональная существующая сессия
        Returns:
            User: Пользователь
        """
        user = await self.get_by_field(session=session, telegram_id=telegram_id)
        
        if not user:
            user_data = {
                "telegram_id": telegram_id,
                "telegram_username": telegram_data.get("username"),
                "name": telegram_data.get("first_name"),
            }
            user = await self.create(user_data, session=session)

        try:
            bot_id = await bot.bot_repo.get_id_by_telegram_id(telegram_bot_id, session=session)
            
            # Проверяем существование связи через прямую проверку в таблице user_bots
            link_exists = await session.execute(
                select(user_bots).where(
                    user_bots.c.user_id == user.id,
                    user_bots.c.bot_id == bot_id
                )
            )
            
            if not link_exists.scalar_one_or_none():
                await session.execute(
                    user_bots.insert().values(
                        user_id=user.id,
                        bot_id=bot_id
                    )
                )
                await session.commit()
        except ValueError as e:
            await session.rollback()
            raise e

        return user


user_repo = UserRepo(User)