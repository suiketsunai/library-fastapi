# sqlalchemy engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# app settings
from ..settings import settings

DATABASE_URL = URL.create(
    drivername=settings.db_drivername,
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_server,
    port=settings.db_port,
    database=settings.db_db,
)

ASYNC_ENGINE = create_async_engine(
    DATABASE_URL,
    echo=True,
)

ASYNC_SESSION = sessionmaker(
    bind=ASYNC_ENGINE,
    class_=AsyncSession,
    future=True,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
