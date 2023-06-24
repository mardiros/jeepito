from messagebus.domain.model import Metadata
from messagebus.service._async.registry import AsyncMessageRegistry
from messagebus.service._async.unit_of_work import AsyncUnitOfWorkTransaction
from tests._async.conftest import (
    AsyncDummyUnitOfWorkWithEvents,
    AsyncEventstreamPublisher,
    AsyncEventstreamTransport,
    DummyCommand,
    DummyEvent,
    DummyModel,
    Repositories,
)


async def listen_command(
    cmd: DummyCommand, uow: AsyncUnitOfWorkTransaction[Repositories]
) -> DummyModel:
    """This command raise an event played by the message bus."""
    foo = DummyModel(id=cmd.id, counter=0)
    foo.messages.append(DummyEvent(id=foo.id, increment=10))
    await uow.foos.add(foo)
    return foo


async def test_store_events_and_publish(
    bus: AsyncMessageRegistry[Repositories],
    eventstream_transport: AsyncEventstreamTransport,
    uow_with_eventstore: AsyncDummyUnitOfWorkWithEvents,
    dummy_command: DummyCommand,
):
    bus.add_listener(DummyCommand, listen_command)
    async with uow_with_eventstore as tuow:
        await bus.handle(dummy_command, tuow)
        await tuow.commit()

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
            "payload": '{"id": "dummy_cmd", "increment": 10}',
            "type": "dummied_v1",
        },
    ]


async def test_store_events_and_rollback(
    bus: AsyncMessageRegistry[Repositories],
    eventstream_transport: AsyncEventstreamTransport,
    uow_with_eventstore: AsyncDummyUnitOfWorkWithEvents,
    dummy_command: DummyCommand,
):
    bus.add_listener(DummyCommand, listen_command)
    async with uow_with_eventstore as tuow:
        await bus.handle(dummy_command, tuow)
        await tuow.rollback()
    assert eventstream_transport.events == []


async def test_store_initialize_transport(
    eventstore: AsyncEventstreamPublisher,
    eventstream_transport: AsyncEventstreamTransport,
):
    await eventstore.initialize()
    assert eventstream_transport.initialized is True
