from messagebus import Command, Event, Field, Metadata


class RegisterBook(Command):
    id: str = Field(...)
    isbn: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    metadata: Metadata = Metadata(name="register_book", schema_version=1)


class BookRegistered(Event):
    isbn: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    metadata: Metadata = Metadata(
        name="register_book", schema_version=1, published=True
    )


class CreateReviewer(Command):
    id: str = Field(...)
    nickname: str = Field(...)
    metadata: Metadata = Metadata(name="create_review", schema_version=1)


class ReviewerCreated(Command):
    id: str = Field(...)
    nickname: str = Field(...)
    metadata: Metadata = Metadata(
        name="reviewer_created", schema_version=1, published=True
    )


class CreateReview(Command):
    id: str = Field(...)
    reviewer_id: str = Field(...)
    book_id: str = Field(...)
    rate: int = Field(...)
    comment: str = Field(...)
    metadata: Metadata = Metadata(name="create_review", schema_version=1)


class ReviewCreated(Command):
    id: str = Field(...)
    reviewer_id: str = Field(...)
    book_id: str = Field(...)
    rate: int = Field(...)
    comment: str = Field(...)
    metadata: Metadata = Metadata(
        name="create_review", schema_version=1, published=True
    )
