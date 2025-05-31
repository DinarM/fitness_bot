from sqlalchemy import select
from app.db.models import User, UserBot
from app.repo import bot_token
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

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
                'last_name': telegram_data.get("last_name"),
            }
            user = await self.create(user_data, session=session)
        else:
            # Проверяем, изменились ли данные пользователя
            update_data = {}
            if user.telegram_username != telegram_data.get("username"):
                update_data["telegram_username"] = telegram_data.get("username")
            if user.name != telegram_data.get("first_name"):
                update_data["name"] = telegram_data.get("first_name")
            if user.last_name != telegram_data.get("last_name"):
                update_data["last_name"] = telegram_data.get("last_name")
                
            if update_data:
                user = await self.update(user.id, update_data, session=session)

        try:
            bot_id = await bot_token.bot_repo.get_id_by_telegram_id(telegram_bot_id, session=session)

            # ORM-проверка существования связи и вставка через UserBot
            existing_link = await session.execute(
                select(UserBot).where(
                    UserBot.user_id == user.id,
                    UserBot.bot_id == bot_id
                )
            )
            if not existing_link.scalar_one_or_none():
                session.add(UserBot(user_id=user.id, bot_id=bot_id))
                await session.commit()
        except ValueError as e:
            await session.rollback()
            raise e

        return user

    @with_session
    async def get_user_by_telegram_id(
        self,
        telegram_id: int, 
        session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        """
        Получает пользователя по его Telegram ID
        Args:
            telegram_id: Telegram ID пользователя
            session: Опциональная существующая сессия
        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        return await self.get_by_field(session=session, telegram_id=telegram_id)
    
    @with_session
    async def check_user_is_admin(
        self, 
        user_id: int, 
        bot_id: int, 
        session: Optional[AsyncSession] = None
    ) -> bool:
        """
        Проверяет, является ли пользователь администратором бота
        Args:
            user_id: ID пользователя
            bot_id: ID бота
            session: Опциональная существующая сессия
        Returns:
            bool: True если пользователь администратор, иначе False
        """
        result = await session.execute(
            select(UserBot.is_admin).where(
                UserBot.user_id == user_id,
                UserBot.bot_id == bot_id
            )
        )
        return result.scalar_one_or_none() is True
    
    @with_session
    async def get_bot_users(
        self,
        bot_id,
        session: Optional[AsyncSession] = None
    ) -> list[tuple[User, bool]]:
        """
        Получает список пользователей бота с их правами администратора
        Args:
            bot_id: ID бота
            session: Опциональная существующая сессия
        Returns:
            list[tuple[User, bool]]: Список кортежей (пользователь, флаг админа)
        """
        result = await session.execute(
            select(User, UserBot.is_admin)
            .join(UserBot, User.id == UserBot.user_id)
            .where(UserBot.bot_id == bot_id)
        )
        return result.all()

 
user_repo = UserRepo(User)