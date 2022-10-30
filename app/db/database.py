# uuid generation
from uuid import uuid4

# asyncpg connection
from asyncpg import Connection

# sqlalchemy engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# app settings
from ..settings import settings


class CustomConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


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
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "connection_class": CustomConnection,
    },
)

ASYNC_SESSION = sessionmaker(
    bind=ASYNC_ENGINE,
    class_=AsyncSession,
    future=True,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
