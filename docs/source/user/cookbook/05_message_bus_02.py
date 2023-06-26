from reading_club.domain.messages import RegisterBook
from reading_club.domain.model import Book
from reading_club.service.uow import AbstractUnitOfWork

from messagebus import AsyncMessageBus


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
        await trans.commit()
