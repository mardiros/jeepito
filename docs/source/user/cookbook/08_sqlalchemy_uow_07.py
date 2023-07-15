from reading_club.domain.model import Book
from reading_club.service.repositories import (
    AbstractBookRepository,
    BookRepositoryError,
    BookRepositoryOperationResult,
    BookRepositoryResult,
)
from result import Err, Ok
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from . import orm


class SQLBookRepository(AbstractBookRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, model: Book) -> BookRepositoryOperationResult:
        qry = insert(orm.books).values([model.dict(exclude={"messages"})])
        try:
            await self.session.execute(qry)
        except IntegrityError:
            return Err(BookRepositoryError.integrity_error)

        self.seen.append(model)
        return Ok(...)

    async def by_id(self, id: str) -> BookRepositoryResult:
        raise NotImplementedError
