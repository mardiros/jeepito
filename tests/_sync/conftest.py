import enum
from typing import Any, MutableMapping, Type

import pytest
from pydantic import Field
from result import Err, Ok, Result

from messagebus.domain.model import Model
from messagebus.service._sync.registry import SyncMessageRegistry
from messagebus.service._sync.repository import SyncAbstractRepository
from messagebus.service._sync.unit_of_work import SyncAbstractUnitOfWork

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


class SyncDummyRepository(SyncAbstractRepository[DummyModel]):
    models: MutableMapping[str, DummyModel]

    def __init__(self) -> None:
        self.seen = []
        self.initialized = False
        self.models = {}

    def initialize(self) -> None:
        self.initialized = True

    def add(self, model: DummyModel) -> DummyRepositoryOperationResult:
        if model.id in self.models:
            return Err(DummyError.integrity_error)
        self.models[model.id] = model
        self.seen.append(model)
        return Ok(...)

    def get(self, id: str) -> DummyRepositoryResult:
        try:
            return Ok(self.models[id])
        except KeyError:
            return Err(DummyError.not_found)


class SyncDummyUnitOfWork(SyncAbstractUnitOfWork):
    foos = SyncDummyRepository()
    bars = SyncDummyRepository()

    def __init__(self) -> None:
        super().__init__()
        self.status = "init"

    def commit(self) -> None:
        """Commit the transation."""
        self.status = "committed"

    def rollback(self) -> None:
        """Rollback the transation."""
        self.status = "aborted"


@pytest.fixture
def foo_factory() -> Type[DummyModel]:
    return DummyModel


@pytest.fixture
def async_uow() -> SyncAbstractUnitOfWork:
    return SyncDummyUnitOfWork()


@pytest.fixture
def bus() -> SyncMessageRegistry:
    return SyncMessageRegistry()
