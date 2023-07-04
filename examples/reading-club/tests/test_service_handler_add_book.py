from reading_club.domain.messages import BookRegistered, RegisterBook
from reading_club.domain.model import Book
from reading_club.service.handlers.book import register_book
from reading_club.service.repositories import BookRepositoryError
from reading_club.service.uow import AbstractUnitOfWork

from messagebus import AsyncMessageBus


async def test_register_book(register_book_cmd: RegisterBook, uow: AbstractUnitOfWork):
    async with uow as t:
        operation = await register_book(register_book_cmd, t)
        assert operation is not None
        assert operation.is_ok()
        book = await t.books.by_id(register_book_cmd.id)
        assert book.is_ok()
        assert book.unwrap() == Book(
            id="x",
            title="Domain Driven Design",
            author="Eric Evans",
            isbn="0-321-12521-5",
        )
        assert book.unwrap().messages == [
            BookRegistered(
                id="x",
                isbn="0-321-12521-5",
                title="Domain Driven Design",
                author="Eric Evans",
            )
        ]
        await t.commit()

    async with uow as t:
        operation = await register_book(register_book_cmd, t)
        assert operation is not None
        assert operation.is_err()
        assert operation.unwrap_err() == BookRepositoryError.integrity_error
        await t.rollback()


async def test_bus_handler(
    bus: AsyncMessageBus, register_book_cmd: RegisterBook, uow: AbstractUnitOfWork
):
    async with uow as trans:
        await bus.handle(register_book_cmd, trans)
        book = await trans.books.by_id(register_book_cmd.id)
        assert book.is_ok()
        assert book.unwrap() == Book(
            id="x",
            title="Domain Driven Design",
            author="Eric Evans",
            isbn="0-321-12521-5",
        )
        assert book.unwrap().messages == []
        await trans.commit()
