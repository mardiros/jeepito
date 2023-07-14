from reading_club.domain.messages import BookRegistered, RegisterBook
from reading_club.domain.model import Book
from reading_club.service.uow import AbstractUnitOfWork

from messagebus import AsyncMessageBus
from tests.conftest import EventstreamTransport


async def test_bus_handler(
    bus: AsyncMessageBus,
    register_book_cmd: RegisterBook,
    uow: AbstractUnitOfWork,
    transport: EventstreamTransport,
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

    assert uow.eventstore.messages == [  # type: ignore
        RegisterBook(
            id="x",
            isbn="0-321-12521-5",
            title="Domain Driven Design",
            author="Eric Evans",
        ),
        BookRegistered(
            id="x",
            isbn="0-321-12521-5",
            title="Domain Driven Design",
            author="Eric Evans",
        ),
    ]
    assert transport.events == [
        {
            "id": transport.events[0]["id"],
            "created_at": transport.events[0]["created_at"],
            "payload": '{"id": "x", "isbn": "0-321-12521-5", "title": "Domain Driven '
            'Design", "author": "Eric Evans"}',
            "type": "register_book_v1",
        },
    ]
