import abc
from typing import Any, Mapping

from messagebus.domain.model import Message


class AbstractMessageSerializer(abc.ABC):
    """The message serializer take the message and return it with python native types,
    that are serializable for a transport.
    """

    @abc.abstractmethod
    def serialize_message(self, message: Message) -> Mapping[str, Any]:
        """Publish a message to the eventstream."""


class MessageSerializer(AbstractMessageSerializer):
    """Default message serializer"""

    def serialize_message(self, message: Message) -> Mapping[str, Any]:
        """Publish a message to the eventstream."""
        return {
            "id": message.message_id,
            "created_at": message.created_at.isoformat(),
            "type": f"{message.metadata.name}_v{message.metadata.schema_version}",
            "payload": message.json(exclude={"message_id", "created_at", "metadata"}),
        }


class SyncAbstractEventstreamTransport(abc.ABC):
    """
    Transport a message to the event stream.
    """

    @abc.abstractmethod
    def initialize(self) -> None:
        """Use to initialize the transport, usually open a tcp socket."""

    @abc.abstractmethod
    def send_message_serialized(self, event: Mapping[str, Any]) -> None:
        """Publish a serialized message to the eventstream."""


class SyncEventstreamPublisher:
    """
    Publish a message to the event stream.

    :param serializer: Used to serialize the Message
    :param transport: Used to send the serialized message to the eventstream.
    """

    def __init__(
        self,
        serializer: AbstractMessageSerializer,
        transport: SyncAbstractEventstreamTransport,
    ) -> None:
        """Publish a message to the eventstream."""
        self.serializer = serializer
        self.transport = transport

    def initialize(self) -> None:
        """Use to initialize the transport."""
        self.transport.initialize()

    def send_message(self, message: Message) -> None:
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
