import uuid

from reading_club.adapters.uow_sqla.uow import SQLUnitOfWork
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from messagebus import AsyncAbstractEventstreamTransport


async def test_commit(
    sqla_engine: AsyncEngine,
    sqla_session: AsyncSession,
    transport: AsyncAbstractEventstreamTransport,
):
    book_id = str(uuid.uuid4())
    uow = SQLUnitOfWork(transport, sqla_engine)
    async with uow as trans:
        await uow.session.execute(
            text(
                "insert into books(id, title, author, isbn)"
                "values (:id, :title, :author, :isbn)"
            ),
            {
                "id": book_id,
                "title": "Domain Driven Design",
                "author": "Eric Evans",
                "isbn": "0-321-12521-5",
            },
        )
        await trans.commit()

    row = (
        await sqla_session.execute(
            text("select count(*) from books where id = :id"), {"id": book_id}
        )
    ).first()
    assert row is not None
    assert row[0] == 1


async def test_rollback(
    sqla_engine: AsyncEngine,
    sqla_session: AsyncSession,
    transport: AsyncAbstractEventstreamTransport,
):
    book_id = str(uuid.uuid4())
    uow = SQLUnitOfWork(transport, sqla_engine)
    async with uow as trans:
        await trans.session.execute(
            text(
                "insert into books(id, title, author, isbn)"
                "values (:id, :title, :author, :isbn)"
            ),
            {
                "id": book_id,
                "title": "Domain Driven Design",
                "author": "Eric Evans",
                "isbn": "0-321-12521-5",
            },
        )
        await trans.rollback()

    row = (
        await sqla_session.execute(
            text("select count(*) from books where id = :id"), {"id": book_id}
        )
    ).first()
    assert row is not None
    assert row[0] == 0
