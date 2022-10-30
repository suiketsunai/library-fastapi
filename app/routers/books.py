from typing import Optional

# API
from fastapi import APIRouter, Depends, Query

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
from ..db.filters import BookFilter, AuthorFilter

# other dependencies
from ..dependencies import (
    CustomFilterDepends,
    get_session,
    raise_404,
    raise_404_list,
    response_404,
)

router = APIRouter(
    prefix="/books",
    tags=["Book"],
    dependencies=[Depends(get_session)],
)


async def check_authors(session: AsyncSession, author_ids: list[int]):
    return (
        await session.scalars(
            select(models.Author).where(models.Author.id.in_(author_ids))
        )
    ).all()


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
    if not (
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
    ):
        await raise_404("book")
    return book


@router.post(
    "/",
    response_model=schemas.Book_All,
    responses=response_404,
)
async def create_book(
    book: schemas.BookCreate = Depends(),
    publisher_id: int = Query(title="publisher_id"),
    author_ids: list[int] = Query(
        title="authors",
        min_items=1,
        unique_items=True,
        gt=0,
    ),
    session: AsyncSession = Depends(get_session),
):
    if not (publisher := await session.get(models.Publisher, publisher_id)):
        await raise_404("publisher")
    if len(author_ids) == len(
        authors := await check_authors(session, author_ids)
    ):
        session.add(
            new_book := models.Book(
                **book.dict(),
                publisher=publisher,
                authors=authors,
            )
        )
        await session.commit()
        return new_book
    await raise_404_list(
        "author",
        set(author_ids) - set(a.id for a in authors),
    )


@router.put(
    "/{book_id}",
    response_model=schemas.Book_All,
    responses=response_404,
)
async def update_book(
    book_id: int,
    book: schemas.BookCreate = Depends(),
    publisher_id: int = Query(title="publisher_id"),
    author_ids: list[int] = Query(
        title="authors",
        min_items=1,
        unique_items=True,
        gt=0,
    ),
    session: AsyncSession = Depends(get_session),
):
    if not (
        updated_book := await session.get(
            models.Book,
            book_id,
            [
                selectinload(models.Book.authors),
                selectinload(models.Book.publisher),
            ],
            with_for_update=True,
        )
    ):
        await raise_404("book")
    if not (publisher := await session.get(models.Publisher, publisher_id)):
        await raise_404("publisher")
    if len(author_ids) == len(
        authors := await check_authors(session, author_ids)
    ):
        for key, value in book:
            setattr(updated_book, key, value)
        updated_book.publisher, updated_book.authors = publisher, authors
        await session.commit()
        return updated_book
    await raise_404_list(
        "author",
        set(author_ids) - set(a.id for a in authors),
    )


@router.patch(
    "/{book_id}",
    response_model=schemas.Book_All,
    responses=response_404,
)
async def patch_book(
    book_id: int,
    book: schemas.BookPatch = Depends(),
    publisher_id: Optional[int] = Query(None, title="publisher_id"),
    author_ids: Optional[list[int]] = Query(
        None,
        title="authors",
        min_items=1,
        unique_items=True,
        gt=0,
    ),
    session: AsyncSession = Depends(get_session),
):
    if not (
        patched_book := await session.get(
            models.Book,
            book_id,
            [
                selectinload(models.Book.authors),
                selectinload(models.Book.publisher),
            ],
            with_for_update=True,
        )
    ):
        await raise_404("book")
    if publisher_id:
        if publisher := await session.get(models.Publisher, publisher_id):
            patched_book.publisher = publisher
        else:
            await raise_404("publisher")
    if author_ids:
        if len(author_ids) == len(
            authors := await check_authors(session, author_ids)
        ):
            patched_book.authors = authors
        else:
            await raise_404_list(
                "author",
                set(author_ids) - set(a.id for a in authors),
            )
    for key, value in book.dict(exclude_none=True):
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
    if not (
        deleted_book := await session.get(
            models.Book,
            book_id,
            [
                selectinload(models.Book.authors),
                selectinload(models.Book.publisher),
            ],
            with_for_update=True,
        )
    ):
        await raise_404("book")
    await session.delete(deleted_book)
    await session.commit()
    return deleted_book


@router.get(
    "/{book_id}/authors",
    response_model=Page[schemas.Author],
    responses=response_404,
)
async def read_author_books(
    book_id: int,
    _filter: AuthorFilter = CustomFilterDepends(AuthorFilter),
    session: AsyncSession = Depends(get_session),
):
    if not (book := (await session.get(models.Book, book_id))):
        await raise_404("book")
    return await paginate(
        session,
        _filter.sort(
            _filter.filter(
                select(models.Author).where(models.Author.books.contains(book))
            )
        ),
    )
