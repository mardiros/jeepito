from uuid import UUID

from jeepito import Field, Model


class Book(Model):
    id: UUID = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    isbn: str = Field(...)
