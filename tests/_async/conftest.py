import pytest

from messagebus.service._async.registry import AsyncMessageRegistry
from messagebus.service._async.repository import AsyncAbstractRepository
from messagebus.service._async.unit_of_work import AsyncAbstractUnitOfWork


class AsyncDummyRepository(AsyncAbstractRepository):
    def __init__(self) -> None:
        self.messages = []
        self.initialized = False

    async def initialize(self) -> None:
        self.initialized = True


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


@pytest.fixture
def async_uow() -> AsyncAbstractUnitOfWork:
    return AsyncDummyUnitOfWork()


@pytest.fixture
def bus() -> AsyncMessageRegistry:
    return AsyncMessageRegistry()
