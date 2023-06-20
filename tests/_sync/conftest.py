import pytest

from messagebus.service._sync.registry import SyncMessageRegistry
from messagebus.service._sync.repository import SyncAbstractRepository
from messagebus.service._sync.unit_of_work import SyncAbstractUnitOfWork


class SyncDummyRepository(SyncAbstractRepository):
    def __init__(self) -> None:
        self.messages = []
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True


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
def async_uow() -> SyncAbstractUnitOfWork:
    return SyncDummyUnitOfWork()


@pytest.fixture
def bus() -> SyncMessageRegistry:
    return SyncMessageRegistry()
