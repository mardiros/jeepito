from jeepito import Event, Field, Metadata


class BookRegistered(Event):
    id: str = Field(...)
    isbn: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    metadata: Metadata = Metadata(
        name="register_book",
        schema_version=1,
        published=True,
    )
