from app.repo.base import BaseRepo, with_session
from app.db.models import TestUserAnswer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any


class TestUserAnswerRepo(BaseRepo):
    def __init__(self):
        super().__init__(TestUserAnswer)

    @with_session
    async def create_test_result(
        self,
        test_type_id: int,
        user_id: int,
        bot_id: int,
        answers: Dict[str, Any],
        session: Optional[AsyncSession] = None
    ) -> TestUserAnswer:
        """
        Создает запись с результатами теста пользователя
        
        Args:
            test_type_id: ID типа теста
            user_id: ID пользователя
            answers: Словарь с ответами пользователя
            session: Опциональная существующая сессия
            
        Returns:
            TestUserAnswer: Созданная запись
        """
        test_result_data = {
            'test_type_id': test_type_id,
            'user_id': user_id,
            'bot_id': bot_id,
            'answers': answers
        }
        
        return await self.create(test_result_data, session=session)

    @with_session
    async def get_user_test_results(
        self,
        user_id: int,
        test_type_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> list[TestUserAnswer]:
        """
        Получает результаты тестов пользователя
        
        Args:
            user_id: ID пользователя
            test_type_id: Опциональный ID типа теста для фильтрации
            session: Опциональная существующая сессия
            
        Returns:
            list[TestUserAnswer]: Список результатов тестов
        """
        filters = {'user_id': user_id}
        if test_type_id:
            filters['test_type_id'] = test_type_id
            
        return await self.get_multi_by_field(session=session, **filters)


# Создаем экземпляр репозитория
test_user_answer_repo = TestUserAnswerRepo()
