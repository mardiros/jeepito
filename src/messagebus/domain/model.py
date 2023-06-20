"""
Message base classes.

`Command` and `Event` are two types used to handle changes in the model.

"""

from pydantic import BaseModel, Field


class Model(BaseModel):
    """Base class for model."""


class Metadata(BaseModel):
    name: str = Field(...)
    """Name of the schema."""
    schema_version: int = Field(...)
    """Version of the schema."""
    published: bool = Field(default=False)
    """Publish the event to an eventstream."""


class Message(BaseModel):
    """Base class for messaging."""

    metadata: Metadata


class Command(Message):
    """Baseclass for message of type command."""


class Event(Message):
    """Baseclass for message of type event."""
