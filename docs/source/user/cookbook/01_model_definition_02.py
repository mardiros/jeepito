from jeepito import Command, Field, Metadata


class RegisterBook(Command):
    id: str = Field(...)
    isbn: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    metadata: Metadata = Metadata(name="register_book", schema_version=1)
