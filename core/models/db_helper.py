from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from core.config import settings

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = True, echo_pool: bool = False):
        self.engine: AsyncEngine = create_async_engine(url, echo=echo, echo_pool=echo_pool)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    async def dispose(self):
        await self.engine.dispose()

    async def get_async_db(self) ->AsyncGenerator[AsyncSession,None]:
        async with self.session_factory() as session:
            yield session

db_helper = DatabaseHelper(str(settings.db.url),echo=settings.db.echo,echo_pool=settings.db.echo_pool)
