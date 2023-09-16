import abc
from typing import Any, Mapping

from jeepito.domain.model import Message
from jeepito.service.eventstream import AbstractMessageSerializer, MessageSerializer


class AsyncAbstractEventstreamTransport(abc.ABC):
    """
    Transport a message to the event stream.
    """

    @abc.abstractmethod
    async def send_message_serialized(self, message: Mapping[str, Any]) -> None:
        """Publish a serialized message to the eventstream."""


class AsyncSinkholeEventstreamTransport(AsyncAbstractEventstreamTransport):
    """
    Drop all messages.

    By default, the events are not streamed until it is configured to do so.
    """

    async def send_message_serialized(self, message: Mapping[str, Any]) -> None:
        """Do nothing."""


class AsyncEventstreamPublisher:
    """
    Publish a message to the event stream.

    :param serializer: Used to serialize the Message
    :param transport: Used to send the serialized message to the eventstream.
    """

    def __init__(
        self,
        transport: AsyncAbstractEventstreamTransport,
        serializer: AbstractMessageSerializer = MessageSerializer(),
    ) -> None:
        """Publish a message to the eventstream."""
        self.transport = transport
        self.serializer = serializer

    async def send_message(self, message: Message) -> None:
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
        await self.transport.send_message_serialized(evt)
