from result import Ok, Err
from reading_club.domain.model import Book
from reading_club.service.repositories import (
    AbstractBookRepository,
    BookRepositoryError,
    BookRepositoryOperationResult,
    BookRepositoryResult,
)

class InMemoryBookRepository(AbstractBookRepository):
    books = {}
    ix_books_isbn = {}

    async def add(self, model: Book) -> BookRepositoryOperationResult:
        if model.id in self.books:
            return Err(BookRepositoryError.integrity_error)
        if model.isbn in self.ix_books_isbn:
            return Err(BookRepositoryError.integrity_error)
        self.books[model.id] = model
        self.books[model.isbn] = model.id
        return Ok(...)

    async def by_id(self, id: str) -> BookRepositoryResult:
        if id not in self.books:
            return Err(BookRepositoryError.not_found)
        return Ok(self.books[id])
