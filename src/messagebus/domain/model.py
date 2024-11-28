"""
Message base classes.

`Command` and `Event` are two types used to handle changes in the model.

"""

from collections.abc import MutableSequence
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from lastuuid import uuid7
from pydantic import BaseModel, Field


class Metadata(BaseModel):
    name: str = Field(...)
    """Name of the schema."""
    schema_version: int = Field(...)
    """Version of the schema."""
    published: bool = Field(default=False)
    """Publish the event to an eventstream."""


TMetadata = TypeVar("TMetadata", bound=Metadata)


class Message(BaseModel, Generic[TMetadata]):
    """Base class for messaging."""

    message_id: UUID = Field(default_factory=uuid7)
    """Unique identifier of the message."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    """
    Timestamp of the message.

    All messages are kept in order for observability, debug and event replay.
    """
    metadata: TMetadata
    """
    Define extra fields used at serialization.

    While serializing the message, a name and version must be defined to properly
    defined the message. Event if the class is renamed, those constants must be kept
    identically over the time in the codebase.

    metadata are defined statically at the definition of the message.
    """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Message):
            return False
        slf = self.model_dump(exclude={"message_id", "created_at"})
        otr = other.model_dump(exclude={"message_id", "created_at"})
        return slf == otr


class GenericCommand(Message[TMetadata]):
    """Baseclass for message of type command."""


class GenericEvent(Message[TMetadata]):
    """Baseclass for message of type event."""


class GenericModel(BaseModel, Generic[TMetadata]):
    """Base class for model."""

    messages: MutableSequence[Message[TMetadata]] = Field(
        default_factory=list, exclude=True
    )
    """
    List of messages consumed by the unit of work to mutate the repository.

    Those message are ephemeral, published by event handler and consumed
    by the unit of work during the process of an original command.
    """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GenericModel):
            return False
        slf = self.model_dump()
        otr = other.model_dump()
        return slf == otr


Model = GenericModel[Metadata]
Command = GenericCommand[Metadata]
Event = GenericEvent[Metadata]
