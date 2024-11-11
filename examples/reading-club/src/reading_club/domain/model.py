from uuid import UUID

from jeepito import Field, Model


class Book(Model):
    id: UUID = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    isbn: str = Field(...)


class Reviewer(Model):
    id: UUID = Field(...)
    nickname: str = Field(...)


class Review(Model):
    id: UUID = Field(...)
    reviewer_id: str = Field(...)
    book_id: str = Field(...)
    rate: int = Field(ge=0, le=10)
    comment: str = Field(...)
