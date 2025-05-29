from app.db.models import TestType
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repo.bot_token import bot_repo
from app.repo.test_user_answer import test_user_answer_repo

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
        filters = {'bot_id': bot_id, 'deleted_at': None}
        if only_active:
            filters.update({
                'is_active': True
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
    
    @with_session
    async def get_by_id(
        self, 
        test_type_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[TestType]:
        """
        Получает тип теста по его ID
        Args:
            test_type_id: ID типа теста
            session: Опциональная существующая сессия
        Returns:
            Optional[TestType]: Тип теста или None, если не найден
        """
        return await self.get(session=session, obj_id=test_type_id)

    @with_session
    async def get_available_for_user(
        self,
        bot_id: int,
        user_id: int,
        only_active: bool = True,
        session: Optional[AsyncSession] = None
    ) -> List[TestType]:
        """
        Получает список доступных типов тестов для пользователя:
        - если allow_multiple_passes=True, тест всегда доступен
        - если allow_multiple_passes=False и пользователь уже проходил тест, тест не показывается
        """
        all_types = await self.get_by_bot(bot_id, only_active, session=session)
        # Получаем id уже пройденных тестов
        user_answers = await test_user_answer_repo.get_user_test_results(user_id=user_id, session=session)
        passed_type_ids = {answer.test_type_id for answer in user_answers}
        # Фильтруем
        result = []
        for test_type in all_types:
            if test_type.allow_multiple_passes:
                result.append(test_type)
            else:
                if test_type.id not in passed_type_ids:
                    result.append(test_type)
        return result

test_types_repo = TestTypesRepo(TestType)
