from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps
from typing import Optional, Callable, Any, List
from app.db.unit_of_work import UnitOfWork


def with_session(func: Callable) -> Callable:
    """
    Декоратор для автоматической работы с сессиями.
    Если сессия не передана, создает новую через UnitOfWork.
    """
    @wraps(func)
    async def wrapper(self, *args, session: Optional[AsyncSession] = None, **kwargs) -> Any:
        if session:
            return await func(self, *args, session=session, **kwargs)
        else:
            async with self.uow.session() as new_session:
                return await func(self, *args, session=new_session, **kwargs)
    return wrapper


class BaseRepo:

    def __init__(self, model):
        self.model = model
        self.uow = UnitOfWork()

    @with_session
    async def get(
            self,
            obj_id: int,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.db == obj_id
            )
        )
        return db_obj.scalars().first()

    @with_session
    async def get_multi(self, session: AsyncSession):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    @with_session
    async def create(self,
                     obj_in,
                     session: AsyncSession):
        obj_in_data = obj_in
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @with_session
    async def get_by_field(
            self,
            session: AsyncSession,
            **kwargs
    ):
        """
        Generic method to fetch a single record by arbitrary fields.
        Usage: await repo.get_by_field(session, telegram_bot_id=123)
        """
        stmt = select(self.model).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().first()

    @with_session
    async def get_multi_by_field(
            self,
            session: AsyncSession,
            **kwargs
    ) -> List[Any]:
        """
        Generic method to fetch multiple records by arbitrary fields.
        Usage: await repo.get_multi_by_field(session, is_active=True)
        """
        stmt = select(self.model).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().all()
