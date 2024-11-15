from typing import Any

import pytest

from messagebus.service._sync.registry import ConfigurationError, SyncMessageBus
from tests._sync.conftest import (
    DummyCommand,
    DummyEvent,
    DummyModel,
    Repositories,
    SyncUnitOfWorkTransaction,
)

conftest_mod = __name__.replace("test_registry", "conftest")


def listen_command(
    cmd: DummyCommand, uow: SyncUnitOfWorkTransaction[Repositories]
) -> DummyModel:
    """This command raise an event played by the message bus."""
    foo = DummyModel(id=cmd.id, counter=0)
    foo.messages.append(DummyEvent(id=foo.id, increment=10))
    uow.foos.add(foo)
    return foo


def listen_event(cmd: DummyEvent, uow: SyncUnitOfWorkTransaction[Repositories]) -> None:
    """This event is indented to be fire by the message bus."""
    rfoo = uow.foos.get(cmd.id)
    foo = rfoo.unwrap()
    foo.counter += cmd.increment


def test_messagebus(
    bus: SyncMessageBus[Repositories],
    tuow: SyncUnitOfWorkTransaction[Repositories],
):
    """
    Test that the message bus is firing command and event.

    Because we use venusian, the bus only works the event as been
    attached.
    """
    DummyModel.counter = 0

    foo = listen_command(DummyCommand(id="foo"), tuow)
    assert list(tuow.uow.collect_new_events()) == [DummyEvent(id="foo", increment=10)]
    assert (
        DummyModel.counter == 0
    ), "Events raised cannot be played before the attach_listener has been called"

    listen_event(DummyEvent(id="foo", increment=1), tuow)
    assert foo.counter == 1

    foo = bus.handle(DummyCommand(id="foo2"), tuow)
    assert foo is None, "The command cannot raise event before attach_listener"

    bus.add_listener(DummyCommand, listen_command)
    bus.add_listener(DummyEvent, listen_event)

    foo = bus.handle(DummyCommand(id="foo3"), tuow)
    assert foo.counter == 10, (
        "The command should raise an event that is handle by the bus that "
        "will increment the model to 10"
    )

    bus.remove_listener(DummyEvent, listen_event)

    foo = bus.handle(DummyCommand(id="foo4"), tuow)
    assert (
        foo.counter == 0
    ), "The command should raise an event that is not handled anymore "


def test_messagebus_handle_only_message(
    bus: SyncMessageBus[Repositories],
    tuow: SyncUnitOfWorkTransaction[Repositories],
):
    class Msg:
        def __repr__(self):
            return "<msg>"

    with pytest.raises(RuntimeError) as ctx:
        bus.handle(Msg(), tuow)  # type: ignore
    assert str(ctx.value) == "<msg> was not an Event or Command"


def test_messagebus_cannot_register_handler_twice(
    bus: SyncMessageBus[Repositories],
):
    bus.add_listener(DummyCommand, listen_command)
    with pytest.raises(ConfigurationError) as ctx:
        bus.add_listener(DummyCommand, listen_command)
    assert (
        str(ctx.value) == f"<class '{conftest_mod}.DummyCommand'> command "
        "has been registered twice"
    )
    bus.remove_listener(DummyCommand, listen_command)
    bus.add_listener(DummyCommand, listen_command)


def test_messagebus_cannot_register_handler_on_non_message(
    bus: SyncMessageBus[Repositories],
):
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
    bus: SyncMessageBus[Repositories],
):
    with pytest.raises(ConfigurationError) as ctx:
        bus.remove_listener(DummyCommand, listen_command)

    assert (
        str(ctx.value) == f"<class '{conftest_mod}.DummyCommand'> command "
        "has not been registered"
    )

    with pytest.raises(ConfigurationError) as ctx:
        bus.remove_listener(DummyEvent, listen_event)

    assert (
        str(ctx.value) == f"<class '{conftest_mod}.DummyEvent'> event "
        "has not been registered"
    )

    with pytest.raises(ConfigurationError) as ctx:
        bus.remove_listener(object, listen_command)

    assert (
        str(ctx.value)
        == "Invalid usage of the listen decorator: type <class 'object'> "
        "should be a command or an event"
    )


def test_scan(bus: SyncMessageBus[Any]):
    assert bus.commands_registry == {}
    assert bus.events_registry == {}
    bus.scan("tests._sync.handlers")
    from tests._sync.handlers import dummy

    assert DummyCommand in bus.commands_registry
    assert bus.commands_registry[DummyCommand] == dummy.handler

    assert DummyEvent in bus.events_registry
    assert bus.events_registry[DummyEvent] == [dummy.handler_evt1, dummy.handler_evt2]


def test_scan_relative(bus: SyncMessageBus[Any]):
    with pytest.raises(ValueError) as ctx:
        bus.scan("._async.handlers")
    assert (
        str(ctx.value)
        == "scan error: relative package unsupported for ._async.handlers"
    )
