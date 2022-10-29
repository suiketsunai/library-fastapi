# get column types
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String

# get base class
from sqlalchemy.ext.declarative import declarative_base

# get relationship property
from sqlalchemy.orm import relationship

# fix str/repr for models
from sqlalchemy_repr import RepresentableBase

# construct a base class
Base = declarative_base(cls=RepresentableBase)


class AuthorBookAssociation(Base):
    __tablename__ = "author_book_association"

    # M-M relationship between Book and Author
    book_id = Column(ForeignKey("books.id"), primary_key=True)
    author_id = Column(ForeignKey("authors.id"), primary_key=True)


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    name = Column(String, index=True, nullable=False)

    # 1-M relationship with Book
    books = relationship(
        "Book",
        back_populates="publisher",
        foreign_keys="Book.publisher_id",
        lazy="raise",
    )


class Author(Base):
    __tablename__ = "authors"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    middle_name = Column(String)

    # M-M relationship with Book
    books = relationship(
        "Book",
        secondary="author_book_association",
        back_populates="authors",
        lazy="raise",
    )


class Book(Base):
    __tablename__ = "books"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
    )
    title = Column(String, index=True, nullable=False)
    year = Column(Integer, index=True, nullable=False)
    pages = Column(Integer)
    edition = Column(Integer)
    description = Column(String)

    # M-M relationship with Author
    authors = relationship(
        "Author",
        secondary="author_book_association",
        back_populates="books",
        lazy="raise",
    )

    publisher_id = Column(ForeignKey("publishers.id"))

    # M-1 relationship with Publisher
    publisher = relationship(
        "Publisher",
        back_populates="books",
        foreign_keys=[publisher_id],
        lazy="raise",
    )
