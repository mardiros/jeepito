from messagebus import Model, Field


class Book(Model):
    id: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    isbn: str = Field(...)
