"""
Message base classes.

`Command` and `Event` are two types used to handle changes in the model.

"""

from datetime import datetime
from typing import Any, MutableSequence
from uuid import uuid1

from pydantic import BaseModel, Field


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid1())


class Metadata(BaseModel):
    name: str = Field(...)
    """Name of the schema."""
    schema_version: int = Field(...)
    """Version of the schema."""
    published: bool = Field(default=False)
    """Publish the event to an eventstream."""


class Message(BaseModel):
    """Base class for messaging."""

    message_id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Metadata

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Message):
            return False
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


class Command(Message):
    """Baseclass for message of type command."""


class Event(Message):
    """Baseclass for message of type event."""


class Model(BaseModel):
    """Base class for model."""

    messages: MutableSequence[Message] = Field(default_factory=list)
    """
    List of messages consumed by the unit of work to mutate the repository.

    Those message are ephemeral, published by event handler and consumed
    by the unit of work during the process of an original command.
    """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Model):
            return False
        slf = self.dict(exclude={"messages"})
        otr = other.dict(exclude={"messages"})
        return slf == otr
