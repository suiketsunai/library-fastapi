# dependency and http status
from fastapi import Depends, status

# exceptions
from fastapi.exceptions import HTTPException, ValidationError

# filters
from fastapi_filter.base.filter import BaseFilterModel, _list_to_str_fields

# pydantic exception and model
from pydantic import ValidationError, create_model

# get sqlalchemy async session
from sqlalchemy.ext.asyncio import AsyncSession

# database schemas
from .db import schemas

# database
from .db.database import ASYNC_SESSION

# define nor found response
response_404 = {status.HTTP_404_NOT_FOUND: {"model": schemas.Message}}


# raise 404
async def raise_404(table: str):
    raise HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "msg": f"No such {table}.",
                "type": f"not_found.{table}",
            }
        ],
    )


# raise 404 list
async def raise_404_list(table: str, ids: list[int]):
    raise HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "msg": f"No such {table}: {ids}.",
                "type": f"not_found.{table}",
            }
        ],
    )


# get async session
async def get_session() -> AsyncSession:
    async with ASYNC_SESSION() as session:
        yield session


def CustomFilterDepends(
    Filter: BaseFilterModel,
    *,
    by_alias: bool = False,
    use_cache: bool = True,
):
    """This is a hack to support lists in filters"""
    fields = _list_to_str_fields(Filter)
    GeneratedFilter: BaseFilterModel = create_model(
        Filter.__class__.__name__, **fields
    )

    class FilterWrapper(GeneratedFilter):
        def filter(self, *args, **kwargs):
            try:
                original_filter = Filter(**self.dict(by_alias=by_alias))
            except ValidationError as e:
                for error in e.errors():
                    error["loc"] = ["query"] + list(error["loc"])
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=e.errors(),
                )
            return original_filter.filter(*args, **kwargs)

        def sort(self, *args, **kwargs):
            try:
                original_filter = Filter(**self.dict(by_alias=by_alias))
            except ValidationError as e:
                for error in e.errors():
                    error["loc"] = ["query"] + list(error["loc"])
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=e.errors(),
                )
            return original_filter.sort(*args, **kwargs)

    return Depends(FilterWrapper, use_cache=use_cache)
