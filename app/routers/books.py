# API
from fastapi import APIRouter, Depends

# pagination
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate

# get sqlalchemy functions
from sqlalchemy import select

# get sqlalchemy async session
from sqlalchemy.ext.asyncio import AsyncSession

# get sqlalchemy loading strategy
from sqlalchemy.orm import selectinload

# database models and schemas
from ..db import models, schemas

# book filter
from ..db.filters import BookFilter

# other dependencies
from ..dependencies import (
    CustomFilterDepends,
    get_session,
    raise_404,
    response_404,
)

router = APIRouter(
    prefix="/books",
    tags=["Book"],
    dependencies=[Depends(get_session)],
)


@router.get(
    "/",
    response_model=Page[schemas.Book_All],
)
async def read_books(
    _filter: BookFilter = CustomFilterDepends(BookFilter),
    session: AsyncSession = Depends(get_session),
):
    return await paginate(
        session,
        _filter.sort(
            _filter.filter(
                select(models.Book).options(
                    selectinload(models.Book.authors),
                    selectinload(models.Book.publisher),
                )
            )
        ),
    )


@router.get(
    "/{book_id}",
    response_model=schemas.Book_All,
    responses=response_404,
)
async def read_book(
    book_id: int,
    session: AsyncSession = Depends(get_session),
):
    if (
        book := (
            await session.get(
                models.Book,
                book_id,
                [
                    selectinload(models.Book.authors),
                    selectinload(models.Book.publisher),
                ],
            )
        )
    ) is None:
        await raise_404("book")
    return book


@router.post(
    "/",
    response_model=schemas.Book,
    responses=response_404,
)
async def create_book(
    book: schemas.BookCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    session.add(new_book := models.Book(**book.dict()))
    await session.commit()
    return new_book


@router.put(
    "/{book_id}",
    response_model=schemas.Book,
    responses=response_404,
)
async def update_book(
    book_id: int,
    book: schemas.BookCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if (
        updated_book := await session.get(
            models.Book,
            book_id,
            with_for_update=True,
        )
    ) is None:
        await raise_404("book")
    for key, value in book:
        setattr(updated_book, key, value)
    await session.commit()
    return updated_book


@router.patch(
    "/{book_id}",
    response_model=schemas.Book,
    responses=response_404,
)
async def patch_book(
    book_id: int,
    book: schemas.BookPatch = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if (
        patched_book := await session.get(
            models.Book,
            book_id,
            with_for_update=True,
        )
    ) is None:
        await raise_404("book")
    for key, value in book.dict(exclude_none=True).items():
        setattr(patched_book, key, value)
    await session.commit()
    return patched_book


@router.delete(
    "/{book_id}",
    response_model=schemas.Book_All,
    responses=response_404,
)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_session),
):
    if (
        deleted_book := await session.get(
            models.Book,
            book_id,
            [selectinload(models.Book.books)],
            with_for_update=True,
        )
    ) is None:
        await raise_404("book")
    await session.delete(deleted_book)
    await session.commit()
    return deleted_book
