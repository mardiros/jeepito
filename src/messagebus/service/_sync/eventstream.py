import abc
from collections.abc import Mapping
from typing import Any

from messagebus.domain.model import Message
from messagebus.service.eventstream import AbstractMessageSerializer, MessageSerializer


class SyncAbstractEventstreamTransport(abc.ABC):
    """
    Transport a message to the event stream.
    """

    @abc.abstractmethod
    def send_message_serialized(self, message: Mapping[str, Any]) -> None:
        """Publish a serialized message to the eventstream."""


class SyncSinkholeEventstreamTransport(SyncAbstractEventstreamTransport):
    """
    Drop all messages.

    By default, the events are not streamed until it is configured to do so.
    """

    def send_message_serialized(self, message: Mapping[str, Any]) -> None:
        """Do nothing."""


default_serializer = MessageSerializer()


class SyncEventstreamPublisher:
    """
    Publish a message to the event stream.

    :param serializer: Used to serialize the Message
    :param transport: Used to send the serialized message to the eventstream.
    """

    def __init__(
        self,
        transport: SyncAbstractEventstreamTransport,
        serializer: AbstractMessageSerializer = default_serializer,
    ) -> None:
        """Publish a message to the eventstream."""
        self.transport = transport
        self.serializer = serializer

    def send_message(self, message: Message[Any]) -> None:
        """
        Publish a message to the eventstream.

        To publish a message in the eventstream, the flag parameter "published" of
        the metadata of the message must be set to true.
        By default, message are not pushed to the queue, given the control of
        private message, such as command, and public event, shared with eventstream
        consumers.
        """
        if not message.metadata.published:
            return
        evt = self.serializer.serialize_message(message)
        self.transport.send_message_serialized(evt)
