from uuid import UUID

from messagebus import Command, Event, Field, Metadata


class RegisterBook(Command):
    id: UUID = Field(...)
    isbn: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    metadata: Metadata = Metadata(name="register_book", schema_version=1)


class BookRegistered(Event):
    id: UUID = Field(...)
    isbn: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    metadata: Metadata = Metadata(
        name="book_registered", schema_version=1, published=True
    )


class CreateReviewer(Command):
    id: UUID = Field(...)
    nickname: str = Field(...)
    metadata: Metadata = Metadata(name="create_review", schema_version=1)


class ReviewerCreated(Command):
    id: UUID = Field(...)
    nickname: str = Field(...)
    metadata: Metadata = Metadata(
        name="reviewer_created", schema_version=1, published=True
    )


class CreateReview(Command):
    id: UUID = Field(...)
    reviewer_id: UUID = Field(...)
    book_id: UUID = Field(...)
    rate: int = Field(...)
    comment: str = Field(...)
    metadata: Metadata = Metadata(name="create_review", schema_version=1)


class ReviewCreated(Command):
    id: UUID = Field(...)
    reviewer_id: UUID = Field(...)
    book_id: UUID = Field(...)
    rate: int = Field(...)
    comment: str = Field(...)
    metadata: Metadata = Metadata(
        name="create_review", schema_version=1, published=True
    )
