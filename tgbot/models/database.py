from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from tgbot.config import load_config
from aiogram import Router

router = Router()

Base: DeclarativeMeta = declarative_base()


async def create_pool(
        connection_uri: str = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}",
):
    config = load_config('bot.ini').db_config
    connection_uri = connection_uri.format(user=config.user, password=config.password, port=config.port,
                                           database=config.database, host=config.host)
    engine = create_async_engine(url=make_url(connection_uri))
    pool = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    return pool


@router.startup()
async def on_startup():

    session: Session = router.pool()

    try:
        async with session.bind.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    finally:
        await session.close()
