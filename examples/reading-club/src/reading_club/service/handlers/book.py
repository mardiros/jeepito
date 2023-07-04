from reading_club.domain.messages import BookRegistered, RegisterBook
from reading_club.domain.model import Book
from reading_club.service.repositories import (
    BookRepositoryOperationResult,
)

from messagebus import async_listen

from reading_club.service.uow import AbstractUnitOfWork


@async_listen
async def register_book(
    cmd: RegisterBook, uow: AbstractUnitOfWork
) -> BookRepositoryOperationResult:
    book = Book(id=cmd.id, title=cmd.title, author=cmd.author, isbn=cmd.isbn)
    op = await uow.books.add(book)
    book.messages.append(
        BookRegistered(id=cmd.id, title=cmd.title, author=cmd.author, isbn=cmd.isbn)
    )
    return op
