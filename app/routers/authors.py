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

# author filter
from ..db.filters import AuthorFilter

# other dependencies
from ..dependencies import (
    CustomFilterDepends,
    get_session,
    raise_404,
    response_404,
)

router = APIRouter(
    prefix="/authors",
    tags=["Author"],
    dependencies=[Depends(get_session)],
)


@router.get(
    "/",
    response_model=Page[schemas.Author_Books],
)
async def read_authors(
    _filter: AuthorFilter = CustomFilterDepends(AuthorFilter),
    session: AsyncSession = Depends(get_session),
):
    return await paginate(
        session,
        _filter.sort(
            _filter.filter(
                select(models.Author).options(selectinload(models.Author.books))
            )
        ),
    )


@router.get(
    "/{author_id}",
    response_model=schemas.Author_Books,
    responses=response_404,
)
async def read_author(
    author_id: int,
    session: AsyncSession = Depends(get_session),
):
    if not (
        author := (
            await session.get(
                models.Author,
                author_id,
                [selectinload(models.Author.books)],
            )
        )
    ):
        await raise_404("author")
    return author


@router.post(
    "/",
    response_model=schemas.Author,
    responses=response_404,
)
async def create_author(
    author: schemas.AuthorCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    session.add(new_author := models.Author(**author.dict()))
    await session.commit()
    return new_author


@router.put(
    "/{author_id}",
    response_model=schemas.Author,
    responses=response_404,
)
async def update_author(
    author_id: int,
    author: schemas.AuthorCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if not (
        updated_author := await session.get(
            models.Author,
            author_id,
            with_for_update=True,
        )
    ):
        await raise_404("author")
    for key, value in author:
        setattr(updated_author, key, value)
    await session.commit()
    return updated_author


@router.patch(
    "/{author_id}",
    response_model=schemas.Author,
    responses=response_404,
)
async def patch_author(
    author_id: int,
    author: schemas.AuthorPatch = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if not (
        patched_author := await session.get(
            models.Author,
            author_id,
            with_for_update=True,
        )
    ):
        await raise_404("author")
    for key, value in author.dict(exclude_none=True).items():
        setattr(patched_author, key, value)
    await session.commit()
    return patched_author


@router.delete(
    "/{author_id}",
    response_model=schemas.Author_Books,
    responses=response_404,
)
async def delete_author(
    author_id: int,
    session: AsyncSession = Depends(get_session),
):
    if not (
        deleted_author := await session.get(
            models.Author,
            author_id,
            [selectinload(models.Author.books)],
            with_for_update=True,
        )
    ):
        await raise_404("author")
    await session.delete(deleted_author)
    await session.commit()
    return deleted_author
