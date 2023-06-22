import pytest
from pydantic import Field

from messagebus.domain.model import Command, Event, Metadata
from messagebus.service._async.registry import AsyncMessageRegistry, ConfigurationError
from tests._async.conftest import AsyncDummyUnitOfWork, DummyModel


class DummyCommand(Command):
    id: str = Field(...)
    metadata: Metadata = Metadata(name="dummy", schema_version=1)


class DummyEvent(Event):
    id: str = Field(...)
    increment: int = Field(...)
    metadata: Metadata = Metadata(name="dummied", schema_version=1)


async def listen_command(cmd: DummyCommand, uow: AsyncDummyUnitOfWork) -> DummyModel:
    """This command raise an event played by the message bus."""
    foo = DummyModel(id=cmd.id, counter=0)
    foo.messages.append(DummyEvent(id=foo.id, increment=10))
    await uow.foos.add(foo)
    return foo


async def listen_event(cmd: DummyEvent, uow: AsyncDummyUnitOfWork) -> None:
    """This event is indented to be fire by the message bus."""
    rfoo = await uow.foos.get(cmd.id)
    foo = rfoo.unwrap()
    foo.counter += cmd.increment


async def test_messagebus(bus: AsyncMessageRegistry, async_uow: AsyncDummyUnitOfWork):
    """
    Test that the message bus is firing command and event.

    Because we use venusian, the bus only works the event as been
    attached.
    """

    DummyModel.counter = 0

    foo = await listen_command(DummyCommand(id="foo"), async_uow)
    assert list(async_uow.collect_new_events()) == [DummyEvent(id="foo", increment=10)]
    assert (
        DummyModel.counter == 0
    ), "Events raised cannot be played before the attach_listener has been called"

    await listen_event(DummyEvent(id="foo", increment=1), async_uow)
    assert foo.counter == 1

    foo = await bus.handle(DummyCommand(id="foo2"), async_uow)
    assert foo is None, "The command cannot raise event before attach_listener"

    bus.add_listener(DummyCommand, listen_command)
    bus.add_listener(DummyEvent, listen_event)

    foo = await bus.handle(DummyCommand(id="foo3"), async_uow)
    assert foo.counter == 10, (
        "The command should raise an event that is handle by the bus that "
        "will increment the model to 10"
    )

    bus.remove_listener(DummyEvent, listen_event)

    foo = await bus.handle(DummyCommand(id="foo4"), async_uow)
    assert (
        foo.counter == 0
    ), "The command should raise an event that is not handled anymore "


async def test_messagebus_handle_only_message(
    bus: AsyncMessageRegistry, async_uow: AsyncDummyUnitOfWork
):
    class Msg:
        def __repr__(self):
            return "<msg>"

    with pytest.raises(RuntimeError) as ctx:
        await bus.handle(Msg(), async_uow)  # type: ignore
    assert str(ctx.value) == "<msg> was not an Event or Command"


def test_messagebus_cannot_register_handler_twice(bus: AsyncMessageRegistry):
    bus.add_listener(DummyCommand, listen_command)
    with pytest.raises(ConfigurationError) as ctx:
        bus.add_listener(DummyCommand, listen_command)
    assert (
        str(ctx.value) == f"<class '{__name__}.DummyCommand'> command "
        "has been registered twice"
    )
    bus.remove_listener(DummyCommand, listen_command)
    bus.add_listener(DummyCommand, listen_command)


def test_messagebus_cannot_register_handler_on_non_message(bus: AsyncMessageRegistry):
    with pytest.raises(ConfigurationError) as ctx:
        bus.add_listener(
            object,  # type: ignore
            listen_command,
        )
    assert (
        str(ctx.value)
        == "Invalid usage of the listen decorator: type <class 'object'> "
        "should be a command or an event"
    )


def test_messagebus_cannot_unregister_non_unregistered_handler(
    bus: AsyncMessageRegistry,
):
    with pytest.raises(ConfigurationError) as ctx:
        bus.remove_listener(DummyCommand, listen_command)

    assert (
        str(ctx.value) == f"<class '{__name__}.DummyCommand'> command "
        "has not been registered"
    )

    with pytest.raises(ConfigurationError) as ctx:
        bus.remove_listener(DummyEvent, listen_event)

    assert (
        str(ctx.value) == f"<class '{__name__}.DummyEvent'> event "
        "has not been registered"
    )

    with pytest.raises(ConfigurationError) as ctx:
        bus.remove_listener(object, listen_command)

    assert (
        str(ctx.value)
        == "Invalid usage of the listen decorator: type <class 'object'> "
        "should be a command or an event"
    )
