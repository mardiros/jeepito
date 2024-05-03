from jeepito.domain.model import Metadata
from jeepito.service._sync.registry import SyncMessageBus
from jeepito.service._sync.unit_of_work import SyncUnitOfWorkTransaction
from tests._sync.conftest import (
    DummyCommand,
    DummyEvent,
    DummyModel,
    Repositories,
    SyncDummyUnitOfWorkWithEvents,
    SyncEventstreamTransport,
)


def listen_command(
    cmd: DummyCommand, uow: SyncUnitOfWorkTransaction[Repositories]
) -> DummyModel:
    """This command raise an event played by the message bus."""
    foo = DummyModel(id=cmd.id, counter=0)
    foo.messages.append(DummyEvent(id=foo.id, increment=10))
    uow.foos.add(foo)
    return foo


def test_store_events_and_publish(
    bus: SyncMessageBus[Repositories],
    eventstream_transport: SyncEventstreamTransport,
    uow_with_eventstore: SyncDummyUnitOfWorkWithEvents,
    dummy_command: DummyCommand,
):
    bus.add_listener(DummyCommand, listen_command)
    with uow_with_eventstore as tuow:
        bus.handle(dummy_command, tuow)
        tuow.commit()

    assert uow_with_eventstore.eventstore.messages == [  # type: ignore
        DummyCommand(
            metadata=Metadata(name="dummy", schema_version=1, published=False),
            id="dummy_cmd",
        ),
        DummyEvent(
            metadata=Metadata(name="dummied", schema_version=1, published=True),
            id="dummy_cmd",
            increment=10,
        ),
    ]
    evt: DummyEvent = uow_with_eventstore.eventstore.messages[1]  # type: ignore
    assert eventstream_transport.events == [
        {
            "created_at": evt.created_at.isoformat(),
            "id": evt.message_id,
            "payload": '{"id":"dummy_cmd","increment":10}',
            "type": "dummied_v1",
        },
    ]


def test_store_events_and_rollback(
    bus: SyncMessageBus[Repositories],
    eventstream_transport: SyncEventstreamTransport,
    uow_with_eventstore: SyncDummyUnitOfWorkWithEvents,
    dummy_command: DummyCommand,
):
    bus.add_listener(DummyCommand, listen_command)
    with uow_with_eventstore as tuow:
        bus.handle(dummy_command, tuow)
        tuow.rollback()
    assert eventstream_transport.events == []
