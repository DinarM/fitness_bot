from app.db.models import TestAnswer
from app.repo.base import BaseRepo, with_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List


class TestAnswerRepo(BaseRepo):
    @with_session
    async def get_multi_by_test_question(
        self, 
        question_id: int,
        session: Optional[AsyncSession] = None
    ) -> List[TestAnswer]:
        filters = {'question_id': question_id, 'deleted_at': None}

        return await self.get_multi_by_field(session=session, **filters, order_by='order')
    
test_answer_repo = TestAnswerRepo(TestAnswer)