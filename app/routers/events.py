# creating API
from fastapi import APIRouter

# get sqlalchemy functions
from sqlalchemy import func, select

# get database models
from ..db import models

# get async engine
from ..db.database import ASYNC_ENGINE, ASYNC_SESSION

router = APIRouter()


@router.on_event("startup")
async def init_models():
    """Temporary function for creating tables"""
    async with ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    async with ASYNC_SESSION() as session:
        # quit if records exists
        if await session.scalar(select(func.count(models.Book.id))):
            return

        publishers = [
            models.Publisher(
                name="React Exact Publisher",
            ),
            models.Publisher(
                name="Grand 42 Ltd.",
            ),
            models.Publisher(
                name="Издательство МАНРОС",
            ),
        ]

        authors = [
            models.Author(
                first_name="Владислав",
                last_name="Ткаченко",
                middle_name="Юрьевич",
            ),
            models.Author(
                first_name="Уильям",
                last_name="Шекспир",
            ),
            models.Author(
                first_name="Бранимир",
                last_name="Петрович",
            ),
            models.Author(
                first_name="Бунтаро",
                last_name="Футагава",
            ),
            models.Author(
                first_name="Вилхелмиина",
                last_name="Питкянен",
            ),
            models.Author(
                first_name="Пилигримов",
                last_name="Алексей",
                middle_name="Иоганнович",
            ),
        ]

        books = [
            models.Book(
                title="Book 1",
                year=1991,
                pages=138,
                edition=1,
                authors=[authors[0], authors[1]],
                publisher=publishers[0],
            ),
            models.Book(
                title="Book 2",
                year=1993,
                pages=325,
                edition=1,
                authors=[authors[2]],
                publisher=publishers[1],
            ),
            models.Book(
                title="Book 2.2",
                year=1994,
                pages=327,
                edition=2,
                authors=[authors[2]],
                publisher=publishers[1],
            ),
            models.Book(
                title="Book 3",
                year=1994,
                pages=123,
                edition=1,
                authors=[authors[3]],
                publisher=publishers[0],
            ),
            models.Book(
                title="Book 1.2",
                year=1995,
                pages=193,
                edition=2,
                authors=[authors[0], authors[1], authors[4]],
                publisher=publishers[0],
            ),
            models.Book(
                title="Book 4",
                year=1996,
                pages=343,
                edition=1,
                authors=[authors[3], authors[5]],
                publisher=publishers[2],
            ),
        ]

        # Add all records and commit
        session.add_all([*publishers, *authors, *books])
        await session.commit()
