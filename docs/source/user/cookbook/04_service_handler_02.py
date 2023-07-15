from reading_club.domain.messages import RegisterBook
from reading_club.domain.model import Book
from reading_club.service.handlers.book import register_book
from reading_club.service.repositories import BookRepositoryError
from reading_club.service.uow import AbstractUnitOfWork


async def test_register_book(register_book_cmd: RegisterBook, uow: AbstractUnitOfWork):
    async with uow as transaction:
        operation = await register_book(register_book_cmd, transaction)
        assert operation.is_ok()
        book = await transaction.books.by_id(register_book_cmd.id)
        assert book.is_ok()
        assert book.unwrap() == Book(
            id="x",
            title="Domain Driven Design",
            author="Eric Evans",
            isbn="0-321-12521-5",
        )
        await transaction.commit()

    async with uow as transaction:
        operation = await register_book(register_book_cmd, transaction)
        assert operation.is_err()
        assert operation.unwrap_err() == BookRepositoryError.integrity_error
        await transaction.rollback()
