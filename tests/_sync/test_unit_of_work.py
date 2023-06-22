from typing import Type

import pytest

from messagebus.domain.model import Event, Metadata
from tests._sync.conftest import DummyModel, SyncDummyUnitOfWork


class FooCreated(Event):
    id: str
    metadata: Metadata = Metadata(name="foo_created", schema_version=1, published=True)


class BarCreated(Event):
    metadata: Metadata = Metadata(name="bar_created", schema_version=1, published=True)


def test_collect_new_events(
    async_uow: SyncDummyUnitOfWork, foo_factory: Type[DummyModel]
):
    foo = foo_factory(id="1", counter=0)
    foo.messages.append(FooCreated(id="1"))
    bar = foo_factory(id="1", counter=0)
    bar.messages.append(BarCreated())
    foo2 = foo_factory(id="2", counter=0)
    foo2.messages.append(FooCreated(id="2"))

    with async_uow as uow:
        uow.foos.add(foo)
        uow.bars.add(bar)
        uow.foos.add(foo2)
        uow.commit()

    iter = async_uow.collect_new_events()
    assert next(iter) == FooCreated(id="1")
    assert next(iter) == FooCreated(id="2")
    assert next(iter) == BarCreated()
    with pytest.raises(StopIteration):
        next(iter)


def test_initialize(async_uow: SyncDummyUnitOfWork):
    assert async_uow.foos.initialized is False
    assert async_uow.bars.initialized is False
    async_uow.initialize()
    assert async_uow.foos.initialized is True
    assert async_uow.bars.initialized is True
