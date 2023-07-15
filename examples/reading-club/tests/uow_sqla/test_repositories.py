import uuid

import pytest
from reading_club.adapters.uow_sqla import orm
from reading_club.adapters.uow_sqla.uow import SQLUnitOfWork
from reading_club.domain.messages import RegisterBook
from reading_club.domain.model import Book
from reading_club.service.repositories import BookRepositoryError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_book_add_ok(uow: SQLUnitOfWork, book: Book, sqla_session: AsyncSession):
    async with uow as trans:
        res = await uow.books.add(book)
        await trans.commit()

    assert res.is_ok()

    row = (
        await sqla_session.execute(select(orm.books).where(orm.books.c.id == book.id))
    ).first()
    assert row is not None
    assert row._asdict() == book.dict(exclude={"messages"})

    # ensure the message bus can follow the book messages
    assert uow.books.seen == [book]

    async with uow as trans:
        res = await uow.books.add(book)
        await trans.rollback()


@pytest.mark.parametrize(
    "params",
    [
        {
            "commands": [
                RegisterBook(
                    id=str(uuid.uuid4()),
                    title="Domain Driven Design",
                    author="Eric Evans",
                    isbn="0-321-12521-5",
                )
            ]
        }
    ],
)
async def test_book_add_err(uow: SQLUnitOfWork, book: Book, app_state, params):
    book.id = params["commands"][0].id
    async with uow as trans:
        res = await uow.books.add(book)
        assert res.is_err()
        assert res.unwrap_err() == BookRepositoryError.integrity_error
        await trans.rollback()

    # Since it does not work, the bus can't see the book messages.
    assert uow.books.seen == []


async def test_eventstore_add(
    uow: SQLUnitOfWork, register_book_cmd: RegisterBook, sqla_session: AsyncSession
):
    register_book_cmd.id = str(uuid.uuid4())
    async with uow as trans:
        await uow.eventstore.add(register_book_cmd)
        await trans.commit()

    row = (
        await sqla_session.execute(
            select(orm.messages).where(
                orm.messages.c.id == register_book_cmd.message_id
            )
        )
    ).first()
    assert row is not None
    assert row.id == register_book_cmd.message_id
    assert row.created_at == register_book_cmd.created_at
    assert row.metadata == register_book_cmd.metadata
    assert row.payload == {
        "id": register_book_cmd.id,
        "author": "Eric Evans",
        "isbn": "0-321-12521-5",
        "title": "Domain Driven Design",
    }
