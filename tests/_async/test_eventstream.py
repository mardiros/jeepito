from typing import Any, Mapping, MutableSequence

from messagebus.service._async.eventstream import (
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
)
from messagebus.service.eventstream import MessageSerializer
from tests._async.conftest import DummyCommand, DummyEvent


class AsyncDummyEventstreamTransport(AsyncAbstractEventstreamTransport):
    queue: MutableSequence[Mapping[str, Any]]

    def __init__(self) -> None:
        self.queue = []

    async def send_message_serialized(self, event: Mapping[str, Any]) -> None:
        self.queue.append(event)


async def test_send_message(dummy_command: DummyCommand, dummy_event: DummyEvent):
    srlz = MessageSerializer()
    transport = AsyncDummyEventstreamTransport()
    stream = AsyncEventstreamPublisher(transport, srlz)
    await stream.send_message(dummy_command)
    await stream.send_message(dummy_event)

    assert transport.queue == [srlz.serialize_message(dummy_event)]
