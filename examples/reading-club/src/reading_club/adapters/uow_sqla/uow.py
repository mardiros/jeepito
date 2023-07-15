from types import TracebackType
from typing import Optional, Type

from reading_club.domain.model import Book
from reading_club.service.repositories import (
    AbstractBookRepository,
    BookRepositoryError,
    BookRepositoryOperationResult,
    BookRepositoryResult,
)
from reading_club.service.uow import AbstractUnitOfWork
from result import Err, Ok
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from messagebus import (  # AsyncEventstoreAbstractRepository,
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
    AsyncUnitOfWorkTransaction,
    Message,
)
from messagebus.service._async.repository import AsyncEventstoreAbstractRepository

from . import orm


class SQLEventstoreRepository(AsyncEventstoreAbstractRepository):
    def __init__(self, session: AsyncSession, publisher: AsyncEventstreamPublisher):
        super().__init__(publisher)
        self.session = session

    async def _add(self, message: Message) -> None:
        qry = insert(orm.messages).values(
            [
                {
                    "id": message.message_id,
                    "created_at": message.created_at,
                    "metadata": message.metadata.dict(),
                    "payload": message.dict(
                        exclude={"message_id", "created_at", "metadata"}
                    ),
                }
            ]
        )
        await self.session.execute(qry)


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


class SQLUnitOfWork(AbstractUnitOfWork):
    session: AsyncSession

    def __init__(
        self,
        transport: AsyncAbstractEventstreamTransport,
        sqla_engine: AsyncEngine,
    ):
        super().__init__()
        self.sqla_engine = sqla_engine
        self.session_factory = async_sessionmaker(self.sqla_engine, class_=AsyncSession)
        self.transport = transport

    async def __aenter__(self) -> AsyncUnitOfWorkTransaction:
        self.messages = []
        self.session = self.session_factory()
        self.eventstore = SQLEventstoreRepository(
            self.session,
            AsyncEventstreamPublisher(self.transport),
        )
        self.books = SQLBookRepository(self.session)
        ret = await super().__aenter__()
        return ret

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        try:
            await super().__aexit__(exc_type, exc, tb)
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
