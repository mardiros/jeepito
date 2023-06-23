from typing import Any, Mapping, MutableSequence

from messagebus.service._sync.eventstream import (
    SyncAbstractEventstreamTransport,
    SyncEventstreamPublisher,
)
from messagebus.service.eventstream import MessageSerializer
from tests._sync.conftest import DummyCommand, DummyEvent


class SyncDummyEventstreamTransport(SyncAbstractEventstreamTransport):
    queue: MutableSequence[Mapping[str, Any]]

    def __init__(self) -> None:
        self.initialized = False
        self.queue = []

    def initialize(self) -> None:
        self.initialized = True

    def send_message_serialized(self, event: Mapping[str, Any]) -> None:
        if not self.initialized:
            raise IOError("Stream not ready to receive message")
        self.queue.append(event)


def test_send_message(dummy_command: DummyCommand, dummy_event: DummyEvent):
    srlz = MessageSerializer()
    transport = SyncDummyEventstreamTransport()
    stream = SyncEventstreamPublisher(srlz, transport)
    stream.initialize()
    stream.send_message(dummy_command)
    stream.send_message(dummy_event)

    assert transport.queue == [srlz.serialize_message(dummy_event)]
