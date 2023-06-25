from typing import Iterator
import pytest
from result import Ok, Err
from reading_club.domain.model import Book
from reading_club.service.repositories import (
    AbstractBookRepository,
    BookRepositoryError,
    BookRepositoryOperationResult,
)
from reading_club.service.uow import AbstractUnitOfWork
from reading_club.domain.messages import RegisterBook


class InMemoryBookRepository(AbstractBookRepository):
    books = {}
    ix_books_isbn = {}

    def __init__(self) -> None:
        super().__init__()

    async def add(self, model: Book) -> BookRepositoryOperationResult:
        if model.id in self.books:
            return Err(BookRepositoryError.integrity_error)
        if model.isbn in self.ix_books_isbn:
            return Err(BookRepositoryError.integrity_error)
        self.books[model.id] = model
        self.books[model.isbn] = model.id
        return Ok(...)


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.books = InMemoryBookRepository()

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...


@pytest.fixture
def register_book_cmd():
    return RegisterBook(
        id="x",
        title="Domain Driven Design",
        author="Eric Evans",
        isbn="0-321-12521-5",
    )


@pytest.fixture
def uow() -> Iterator[InMemoryUnitOfWork]:
    uow = InMemoryUnitOfWork()
    yield uow
    uow.books.books.clear()  # type: ignore
    uow.books.ix_books_isbn.clear()  # type: ignore
