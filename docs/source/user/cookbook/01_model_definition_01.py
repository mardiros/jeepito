from messagebus import Field, Model


class Book(Model):
    id: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    isbn: str = Field(...)
