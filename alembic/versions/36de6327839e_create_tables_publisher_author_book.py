"""Create tables Publisher, Author, Book

Revision ID: 36de6327839e
Revises: 
Create Date: 2022-10-30 02:00:21.858403

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "36de6327839e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("middle_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_authors_id"), "authors", ["id"], unique=False)
    op.create_index(
        op.f("ix_authors_last_name"), "authors", ["last_name"], unique=False
    )
    op.create_table(
        "publishers",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_publishers_id"), "publishers", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_publishers_name"), "publishers", ["name"], unique=False
    )
    op.create_table(
        "books",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("edition", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "publisher_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["publisher_id"],
            ["publishers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_books_id"), "books", ["id"], unique=False)
    op.create_index(op.f("ix_books_title"), "books", ["title"], unique=False)
    op.create_index(op.f("ix_books_year"), "books", ["year"], unique=False)
    op.create_table(
        "author_book_association",
        sa.Column(
            "book_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.Column(
            "author_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["authors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
        ),
        sa.PrimaryKeyConstraint("book_id", "author_id"),
    )


def downgrade() -> None:
    op.drop_table("author_book_association")
    op.drop_index(op.f("ix_books_year"), table_name="books")
    op.drop_index(op.f("ix_books_title"), table_name="books")
    op.drop_index(op.f("ix_books_id"), table_name="books")
    op.drop_table("books")
    op.drop_index(op.f("ix_publishers_name"), table_name="publishers")
    op.drop_index(op.f("ix_publishers_id"), table_name="publishers")
    op.drop_table("publishers")
    op.drop_index(op.f("ix_authors_last_name"), table_name="authors")
    op.drop_index(op.f("ix_authors_id"), table_name="authors")
    op.drop_table("authors")
