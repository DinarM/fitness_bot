from app.db.models import TestQuestion
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List


class TestQuestionRepo(BaseRepo):
    @with_session
    async def get_by_test_type(
        self, 
        test_type_id: int,
        only_active: bool = True,
        session: Optional[AsyncSession] = None
    ) -> List[TestQuestion]:
        """
        Получает список типов тестов для бота
        Args:
            bot_id: ID бота
            only_active: Получать только активные тесты
            session: Опциональная существующая сессия
        Returns:
            List[TestType]: Список типов тестов
        """
        filters = {'test_type_id': test_type_id, 'deleted_at': None}
        if only_active:
            filters.update({
                'is_active': True
            })

        return await self.get_multi_by_field(session=session, **filters)
    

test_question_repo = TestQuestionRepo(TestQuestion)