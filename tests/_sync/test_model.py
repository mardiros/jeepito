from tests._sync.conftest import (
    DummyCommand,
    DummyEvent,
    DummyModel,
)

conftest_mod = __name__.replace("test_registry", "conftest")


def test_message_eq(dummy_command: DummyCommand, dummy_event: DummyEvent):
    assert dummy_command != dummy_event
    assert dummy_command != object()
    assert dummy_command == DummyCommand(id="dummy_cmd")


def test_model_eq():
    foo = DummyModel(id="foo", counter=0)
    foo2 = DummyModel(id="foo", counter=0)
    foo2.messages.append(DummyEvent(id="foo", increment=1))
    foo3 = DummyModel(id="foo", counter=1)
    assert foo == DummyModel(id="foo", counter=0)
    assert foo == foo2
    assert foo != foo3
    assert foo != object()
