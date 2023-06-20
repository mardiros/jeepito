import pytest

from messagebus.domain.model import Event, Metadata
from tests._sync.conftest import SyncDummyUnitOfWork


class FooCreated(Event):
    metadata: Metadata = Metadata(name="foo_created", schema_version=1, published=True)


class BarCreated(Event):
    metadata: Metadata = Metadata(name="bar_created", schema_version=1, published=True)


def test_collect_new_events(async_uow: SyncDummyUnitOfWork):
    async_uow.foos.messages.append(FooCreated())
    async_uow.bars.messages.append(BarCreated())

    iter = async_uow.collect_new_events()
    assert next(iter) == FooCreated()
    assert next(iter) == BarCreated()
    with pytest.raises(StopIteration):
        next(iter)


def test_initialize(async_uow: SyncDummyUnitOfWork):
    assert async_uow.foos.initialized is False
    assert async_uow.bars.initialized is False
    async_uow.initialize()
    assert async_uow.foos.initialized is True
    assert async_uow.bars.initialized is True
