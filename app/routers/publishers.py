# API
from fastapi import APIRouter, Depends

# get sqlalchemy functions
from sqlalchemy import select

# get sqlalchemy async session
from sqlalchemy.ext.asyncio import AsyncSession

# get sqlalchemy loading strategy
from sqlalchemy.orm import selectinload

# database
from ..db import models, schemas

# dependencies
from ..dependencies import error_json_response, get_session, response_404

router = APIRouter(
    prefix="/publishers",
    tags=["Publisher"],
    dependencies=[Depends(get_session)],
)


@router.get(
    "/",
    response_model=list[schemas.Publisher_Books],
    responses={},
)
async def read_publishers(session: AsyncSession = Depends(get_session)):
    return (
        await session.scalars(
            select(models.Publisher).options(
                selectinload(models.Publisher.books)
            )
        )
    ).all()


@router.get(
    "/{publisher_id}",
    response_model=schemas.Publisher_Books,
    responses=response_404,
)
async def read_publisher(
    publisher_id: int,
    session: AsyncSession = Depends(get_session),
):
    if (
        publisher := (
            await session.get(
                models.Publisher,
                publisher_id,
                [selectinload(models.Publisher.books)],
            )
        )
    ) is None:
        return error_json_response(
            404,
            "No such publisher",
            "not_found.publisher",
        )
    return publisher


@router.post(
    "/",
    response_model=schemas.Publisher,
    responses=response_404,
)
async def create_publisher(
    publisher: schemas.PublisherCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    session.add(new_publisher := models.Publisher(**publisher.dict()))
    await session.commit()
    return new_publisher


@router.put(
    "/{publisher_id}",
    response_model=schemas.Publisher,
    responses=response_404,
)
async def update_publisher(
    publisher_id: int,
    publisher: schemas.PublisherCreate = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if (
        updated_publisher := await session.get(
            models.Publisher,
            publisher_id,
            with_for_update=True,
        )
    ) is None:
        return error_json_response(
            404,
            "No such publisher",
            "not_found.publisher",
        )
    for key, value in publisher:
        setattr(updated_publisher, key, value)
    await session.commit()
    return updated_publisher


@router.patch(
    "/{publisher_id}",
    response_model=schemas.Publisher,
    responses=response_404,
)
async def patch_publisher(
    publisher_id: int,
    publisher: schemas.PublisherPatch = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if (
        patched_publisher := await session.get(
            models.Publisher,
            publisher_id,
            with_for_update=True,
        )
    ) is None:
        return error_json_response(
            404,
            "No such publisher",
            "not_found.publisher",
        )
    for key, value in publisher.dict(exclude_none=True).items():
        setattr(patched_publisher, key, value)
    await session.commit()
    return patched_publisher


@router.delete(
    "/{publisher_id}",
    response_model=schemas.Publisher_Books,
    responses=response_404,
)
async def delete_publisher(
    publisher_id: int,
    session: AsyncSession = Depends(get_session),
):
    if (
        deleted_publisher := await session.get(
            models.Publisher,
            publisher_id,
            [selectinload(models.Publisher.books)],
            with_for_update=True,
        )
    ) is None:
        return error_json_response(
            404,
            "No such publisher",
            "not_found.publisher",
        )
    await session.delete(deleted_publisher)
    await session.commit()
    return deleted_publisher
