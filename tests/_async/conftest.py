import enum
from typing import Any, MutableMapping, Type

import pytest
from pydantic import Field
from result import Err, Ok, Result

from messagebus.domain.model import Command, Event, Metadata, Model
from messagebus.service._async.registry import AsyncMessageRegistry
from messagebus.service._async.repository import AsyncAbstractRepository
from messagebus.service._async.unit_of_work import AsyncAbstractUnitOfWork

try:
    # does not exists in python 3.7
    from types import EllipsisType  # type:ignore
except ImportError:
    EllipsisType = Any  # type:ignore


class DummyError(enum.Enum):
    integrity_error = "integrity_error"
    not_found = "not_found"


class DummyModel(Model):
    id: str = Field()
    counter: int = Field(0)


DummyRepositoryOperationResult = Result[EllipsisType, DummyError]
DummyRepositoryResult = Result[DummyModel, DummyError]


class AsyncDummyRepository(AsyncAbstractRepository[DummyModel]):
    models: MutableMapping[str, DummyModel]

    def __init__(self) -> None:
        self.seen = []
        self.initialized = False
        self.models = {}

    async def initialize(self) -> None:
        self.initialized = True

    async def add(self, model: DummyModel) -> DummyRepositoryOperationResult:
        if model.id in self.models:
            return Err(DummyError.integrity_error)
        self.models[model.id] = model
        self.seen.append(model)
        return Ok(...)

    async def get(self, id: str) -> DummyRepositoryResult:
        try:
            return Ok(self.models[id])
        except KeyError:
            return Err(DummyError.not_found)


class AsyncDummyUnitOfWork(AsyncAbstractUnitOfWork):
    foos = AsyncDummyRepository()
    bars = AsyncDummyRepository()

    def __init__(self) -> None:
        super().__init__()
        self.status = "init"

    async def commit(self) -> None:
        """Commit the transation."""
        self.status = "committed"

    async def rollback(self) -> None:
        """Rollback the transation."""
        self.status = "aborted"


class DummyCommand(Command):
    id: str = Field(...)
    metadata: Metadata = Metadata(name="dummy", schema_version=1)

    def __eq__(self, other: Any):
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


class DummyEvent(Event):
    id: str = Field(...)
    increment: int = Field(...)
    metadata: Metadata = Metadata(name="dummied", schema_version=1, published=True)

    def __eq__(self, other: Any):
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


@pytest.fixture
def foo_factory() -> Type[DummyModel]:
    return DummyModel


@pytest.fixture
def async_uow() -> AsyncAbstractUnitOfWork:
    return AsyncDummyUnitOfWork()


@pytest.fixture
def bus() -> AsyncMessageRegistry:
    return AsyncMessageRegistry()


@pytest.fixture
def dummy_command() -> DummyCommand:
    return DummyCommand(id="dummy_cmd")


@pytest.fixture
def dummy_event() -> DummyEvent:
    return DummyEvent(id="dummy_evt", increment=1)
