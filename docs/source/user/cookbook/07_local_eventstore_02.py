from typing import Iterator

import pytest
from reading_club.service.uow import AbstractUnitOfWork

from messagebus import AsyncAbstractEventstreamTransport, AsyncEventstreamPublisher


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self, transport: AsyncAbstractEventstreamTransport):
        self.books = InMemoryBookRepository()
        self.eventstore = InMemoryEventstoreRepository(
            publisher=AsyncEventstreamPublisher(transport)
        )

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...


@pytest.fixture
def uow(transport: AsyncAbstractEventstreamTransport) -> Iterator[InMemoryUnitOfWork]:
    uow = InMemoryUnitOfWork(transport)
    yield uow
    uow.books.books.clear()  # type: ignore
    uow.books.ix_books_isbn.clear()  # type: ignore
    uow.eventstore.messages.clear()  # type: ignore
