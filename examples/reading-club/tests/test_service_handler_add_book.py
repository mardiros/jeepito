from reading_club.domain.messages import RegisterBook
from reading_club.service.handlers.book import register_book
from reading_club.service.uow import AbstractUnitOfWork
from reading_club.service.repositories import BookRepositoryError


async def test_register_book(register_book_cmd: RegisterBook, uow: AbstractUnitOfWork):
    async with uow as t:
        operation = await register_book(register_book_cmd, t)
        assert operation.is_ok()
        await t.commit()

    async with uow as t:
        operation = await register_book(register_book_cmd, t)
        assert operation.is_err()
        assert operation.unwrap_err() == BookRepositoryError.integrity_error
        await t.rollback()
