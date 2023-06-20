import pytest

from messagebus.domain.model import Event, Metadata
from tests._async.conftest import AsyncDummyUnitOfWork


class FooCreated(Event):
    metadata: Metadata = Metadata(name="foo_created", schema_version=1, published=True)


class BarCreated(Event):
    metadata: Metadata = Metadata(name="bar_created", schema_version=1, published=True)


def test_collect_new_events(async_uow: AsyncDummyUnitOfWork):
    async_uow.foos.messages.append(FooCreated())
    async_uow.bars.messages.append(BarCreated())

    iter = async_uow.collect_new_events()
    assert next(iter) == FooCreated()
    assert next(iter) == BarCreated()
    with pytest.raises(StopIteration):
        next(iter)


async def test_initialize(async_uow: AsyncDummyUnitOfWork):
    assert async_uow.foos.initialized is False
    assert async_uow.bars.initialized is False
    await async_uow.initialize()
    assert async_uow.foos.initialized is True
    assert async_uow.bars.initialized is True
