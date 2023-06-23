from typing import Any, Type

import pytest

from messagebus.domain.model import Event, Metadata
from tests._async.conftest import AsyncDummyUnitOfWork, DummyModel


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


async def test_collect_new_events(
    async_uow: AsyncDummyUnitOfWork, foo_factory: Type[DummyModel]
):
    foo = foo_factory(id="1", counter=0)
    foo.messages.append(FooCreated(id="1"))
    bar = foo_factory(id="1", counter=0)
    bar.messages.append(BarCreated())
    foo2 = foo_factory(id="2", counter=0)
    foo2.messages.append(FooCreated(id="2"))

    async with async_uow as uow:
        await uow.foos.add(foo)
        await uow.bars.add(bar)
        await uow.foos.add(foo2)
        await uow.commit()

    iter = async_uow.collect_new_events()
    assert next(iter) == FooCreated(id="1")
    assert next(iter) == FooCreated(id="2")
    assert next(iter) == BarCreated()
    with pytest.raises(StopIteration):
        next(iter)


async def test_initialize(async_uow: AsyncDummyUnitOfWork):
    assert async_uow.foos.initialized is False
    assert async_uow.bars.initialized is False
    await async_uow.initialize()
    assert async_uow.foos.initialized is True
    assert async_uow.bars.initialized is True
