import abc
from collections.abc import Mapping
from typing import Any

from messagebus.domain.model import Message


class AbstractMessageSerializer(abc.ABC):
    """The message serializer take the message and return it with python native types,
    that are serializable for a transport.
    """

    @abc.abstractmethod
    def serialize_message(self, message: Message[Any]) -> Mapping[str, Any]:
        """Publish a message to the eventstream."""


class MessageSerializer(AbstractMessageSerializer):
    """Default message serializer"""

    def serialize_message(self, message: Message[Any]) -> Mapping[str, Any]:
        """Publish a message to the eventstream."""
        return {
            "id": str(message.message_id),
            "created_at": message.created_at.isoformat(),
            "type": f"{message.metadata.name}_v{message.metadata.schema_version}",
            "payload": message.model_dump_json(
                exclude={"message_id", "created_at", "metadata"}
            ),
        }
