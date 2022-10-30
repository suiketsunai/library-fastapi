# http statuts, dependency
from fastapi import Depends, status

# exceptions
from fastapi.exceptions import HTTPException, ValidationError

# filters
from fastapi_filter.base.filter import BaseFilterModel, _list_to_str_fields

# pydantic exception and model
from pydantic import ValidationError, create_model

# creating session
from sqlalchemy.ext.asyncio import AsyncSession

# get schema
from .db import schemas

# database
from .db.database import ASYNC_SESSION

# define nor found response
response_404 = {404: {"model": schemas.Message}}

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
