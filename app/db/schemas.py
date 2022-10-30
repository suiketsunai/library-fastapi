from typing import Optional

from pydantic import BaseModel, Field

# errors


class ErrorDetails(BaseModel):
    msg: str = Field(title="Message")
    type: str = Field(title="Error Type")


class Message(BaseModel):
    detail: Optional[list[ErrorDetails]]


# publisher


class PublisherAuto(BaseModel):
    id: int


class PublisherBase(BaseModel):
    name: str


class PublisherCreate(PublisherBase):
    pass


class PublisherPatch(PublisherBase):
    name: Optional[str]


class Publisher(PublisherBase, PublisherAuto):
    class Config:
        orm_mode = True


# author


class AuthorAuto(BaseModel):
    id: int


class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorPatch(AuthorBase):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]


class Author(AuthorBase, AuthorAuto):
    class Config:
        orm_mode = True


# book


class BookAuto(BaseModel):
    id: int


class BookBase(BaseModel):
    title: str
    year: int
    description: Optional[str] = None
    pages: Optional[int] = None
    edition: Optional[int] = None


class BookCreate(BookBase):
    publisher_id: int


class Book(BookBase, BookAuto):
    class Config:
        orm_mode = True


# models with lists


class Book_Authors(Book):
    authors: list[Author] = Field(min_items=1, unique_items=True)


class Book_Publisher(Book):
    publisher: Publisher


class Book_All(Book_Authors, Book_Publisher):
    pass


class Author_Books(Author):
    books: Optional[list[Book]] = Field([], unique_items=True)


class Author_Books_Publisher(Author):
    books: Optional[list[Book_Publisher]] = Field([], unique_items=True)


class Publisher_Books(Publisher):
    books: Optional[list[Book]] = Field([], unique_items=True)


class Publisher_Books_Authors(Publisher):
    books: Optional[list[Book_Authors]] = Field([], unique_items=True)
