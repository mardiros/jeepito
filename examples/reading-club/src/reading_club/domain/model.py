from messagebus import Field, Model


class Book(Model):
    id: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    isbn: str = Field(...)


class Reviewer(Model):
    id: str = Field(...)
    nickname: str = Field(...)


class Review(Model):
    id: str = Field(...)
    reviewer_id: str = Field(...)
    book_id: str = Field(...)
    rate: int = Field(ge=0, le=10)
    comment: str = Field(...)
