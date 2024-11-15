from collections.abc import Iterator, MutableSequence
from typing import Any, ClassVar
from uuid import UUID

import pytest
from reading_club.domain.model import Book
from reading_club.service.repositories import (
    AbstractBookRepository,
    AsyncEventstoreAbstractRepository,
    BookRepositoryError,
    BookRepositoryOperationResult,
    BookRepositoryResult,
)
from reading_club.service.uow import AbstractUnitOfWork
from result import Err, Ok

from messagebus import (
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
    Message,
)


class InMemoryEventstoreRepository(AsyncEventstoreAbstractRepository):
    messages: ClassVar[MutableSequence[Message[Any]]] = []

    async def _add(self, message: Message[Any]) -> None:
        self.messages.append(message)


class InMemoryBookRepository(AbstractBookRepository):
    books: ClassVar[dict[UUID, Book]] = {}
    ix_books_isbn: ClassVar[dict[str, UUID]] = {}

    async def add(self, model: Book) -> BookRepositoryOperationResult:
        if model.id in self.books:
            return Err(BookRepositoryError.integrity_error)
        if model.isbn in self.ix_books_isbn:
            return Err(BookRepositoryError.integrity_error)
        self.books[model.id] = model
        self.ix_books_isbn[model.isbn] = model.id
        self.seen.append(model)
        return Ok(...)

    async def by_id(self, id: UUID) -> BookRepositoryResult:
        if id not in self.books:
            return Err(BookRepositoryError.not_found)
        return Ok(self.books[id])


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self, transport: AsyncAbstractEventstreamTransport):
        self.books = InMemoryBookRepository()
        self.eventstore = InMemoryEventstoreRepository(
            publisher=AsyncEventstreamPublisher(transport)
        )

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


@pytest.fixture
def uow(transport: AsyncAbstractEventstreamTransport) -> Iterator[InMemoryUnitOfWork]:
    uow = InMemoryUnitOfWork(transport)
    yield uow
    uow.books.books.clear()  # type: ignore
    uow.books.ix_books_isbn.clear()  # type: ignore
    uow.eventstore.messages.clear()  # type: ignore
