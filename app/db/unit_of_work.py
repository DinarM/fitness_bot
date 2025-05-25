
from contextlib import asynccontextmanager
from app.db.database import AsyncSessionLocal

class UnitOfWork:
    def __init__(self):
        self._session = AsyncSessionLocal

    @asynccontextmanager
    async def session(self):
        """Generate new session."""
        async with self._session() as session:
            try:
                yield session
            except:
                await session.rollback()
                raise
            finally:
                await session.close()