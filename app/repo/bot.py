from sqlalchemy import select
from app.db.models import BotToken
from app.repo.base import BaseRepo
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class BotRepo(BaseRepo):
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

    async def get_by_token(self, token: str, session: Optional[AsyncSession] = None) -> Optional[BotToken]:
        """
        Получает бота по токену
        Args:
            token: Токен бота
            session: Опциональная существующая сессия
        Returns:
            Optional[BotToken]: Бот или None если не найден
        """
        return await self.get_by_field(session=session, token=token)

    async def create(self, token: str, username: str, user_id: int, session: Optional[AsyncSession] = None) -> int:
        """
        Создает нового бота
        Args:
            token: Токен бота
            username: Имя пользователя бота
            user_id: ID владельца бота
            session: Опциональная существующая сессия
        Returns:
            int: ID созданного бота
        """
        bot_data = {
            "token": token,
            "bot_username": username,
            "user_id": user_id,
            "is_active": True
        }
        bot = await self.create(bot_data, session=session)
        return bot.id

    async def check_bot_exists(self, user_id: int, session: Optional[AsyncSession] = None) -> bool:
        """
        Проверяет, есть ли у пользователя бот
        Args:
            user_id: ID пользователя
            session: Опциональная существующая сессия
        Returns:
            bool: True если у пользователя есть бот
        """
        bot = await self.get_by_field(session=session, user_id=user_id, is_active=True)
        return bot is not None


bot_repo = BotRepo(BotToken)