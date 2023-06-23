from typing import Any, Type

import pytest

from messagebus.domain.model import Event, Metadata
from tests._sync.conftest import SyncDummyUnitOfWork, DummyModel


class FooCreated(Event):
    id: str
    metadata: Metadata = Metadata(name="foo_created", schema_version=1, published=True)

    def __eq__(self, other: Any):
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


class BarCreated(Event):
    metadata: Metadata = Metadata(name="bar_created", schema_version=1, published=True)

    def __eq__(self, other: Any):
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


def test_collect_new_events(
    uow: SyncDummyUnitOfWork, foo_factory: Type[DummyModel]
):
    foo = foo_factory(id="1", counter=0)
    foo.messages.append(FooCreated(id="1"))
    bar = foo_factory(id="1", counter=0)
    bar.messages.append(BarCreated())
    foo2 = foo_factory(id="2", counter=0)
    foo2.messages.append(FooCreated(id="2"))

    with uow as tuow:
        tuow.foos.add(foo)
        tuow.bars.add(bar)
        tuow.foos.add(foo2)
        tuow.commit()

    iter = uow.collect_new_events()
    assert next(iter) == FooCreated(id="1")
    assert next(iter) == FooCreated(id="2")
    assert next(iter) == BarCreated()
    with pytest.raises(StopIteration):
        next(iter)


def test_initialize(uow: SyncDummyUnitOfWork):
    assert uow.foos.initialized is False
    assert uow.bars.initialized is False
    uow.initialize()
    assert uow.foos.initialized is True
    assert uow.bars.initialized is True
