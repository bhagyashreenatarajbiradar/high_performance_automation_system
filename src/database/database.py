
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./automation.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    from src.models.task import Task
    from src.models.execution_history import ExecutionHistory

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

