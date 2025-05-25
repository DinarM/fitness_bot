from sqlalchemy import select, true
from app.db.models import TestType
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repo.bot import bot_repo

class TestTypesRepo(BaseRepo):
    @with_session
    async def get_by_bot(
        self, 
        bot_id: int,
        only_active: bool = True,
        session: Optional[AsyncSession] = None
    ) -> List[TestType]:
        """
        Получает список типов тестов для бота
        Args:
            bot_id: ID бота
            only_active: Получать только активные тесты
            session: Опциональная существующая сессия
        Returns:
            List[TestType]: Список типов тестов
        """
        filters = {'bot_id': bot_id}
        if only_active:
            filters.update({
                'is_active': True,
                'deleted_at': None
            })
        return await self.get_multi_by_field(session=session, **filters)

    @with_session
    async def get_by_telegram_bot(
        self, 
        telegram_bot_id: int,
        only_active: bool = True,
        session: Optional[AsyncSession] = None
    ) -> List[TestType]:
        """
        Получает список типов тестов для бота по его telegram_id
        Args:
            telegram_bot_id: Telegram ID бота
            only_active: Получать только активные тесты
            session: Опциональная существующая сессия
        Returns:
            List[TestType]: Список типов тестов
        """
        bot_id = await bot_repo.get_id_by_telegram_id(telegram_bot_id, session=session)
        return await self.get_by_bot(bot_id, only_active, session=session)


test_types_repo = TestTypesRepo(TestType)
