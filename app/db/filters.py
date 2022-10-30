from typing import Optional

# get filter class
from fastapi_filter.contrib.sqlalchemy import Filter

# get validator for restrictions
from pydantic import validator

# get models
from . import models


def check_fields(banned_fields: list[str], fields: list[str]):
    for field in fields:
        if field.replace("+", "").replace("-", "") in banned_fields:
            raise ValueError(f"You can't sort by: {', '.join(banned_fields)}")
    return fields


class AuthorFilter(Filter):
    first_name__ilike: Optional[str]
    last_name__ilike: Optional[str]
    middle_name__ilike: Optional[str]

    order_by: Optional[list[str]]

    class Constants(Filter.Constants):
        model = models.Author

    @validator("order_by")
    def restrict_sortable_fields(cls, value):
        return check_fields(["books"], value) if value else None


class BookFilter(Filter):
    title__ilike: Optional[str]
    year: Optional[int]
    year__lt: Optional[int]
    year__gte: Optional[int]
    pages: Optional[int]
    pages__lt: Optional[int]
    pages__gte: Optional[int]
    edition: Optional[int]
    edition__lt: Optional[int]
    edition__gte: Optional[int]
    description__ilike: Optional[str]

    order_by: Optional[list[str]]

    class Constants(Filter.Constants):
        model = models.Book

    @validator("order_by")
    def restrict_sortable_fields(cls, value):
        return check_fields(["authors"], value) if value else None


class PublisherFilter(Filter):
    name__ilike: Optional[str]

    order_by: Optional[list[str]]

    class Constants(Filter.Constants):
        model = models.Publisher

    @validator("order_by")
    def restrict_sortable_fields(cls, value):
        return check_fields(["books"], value) if value else None
