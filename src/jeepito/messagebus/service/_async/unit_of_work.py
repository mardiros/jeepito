"""Unit of work"""
from __future__ import annotations

import abc
import enum
from types import TracebackType
from typing import Any, Generic, Iterator, Optional, Type, TypeVar

from jeepito.domain.model import Message
from jeepito.service._async.repository import (
    AsyncAbstractRepository,
    AsyncEventstoreAbstractRepository,
    AsyncSinkholeEventstoreRepository,
)


class TransactionError(RuntimeError):
    """A runtime error raised if the transaction lifetime is inappropriate."""


class TransactionStatus(enum.Enum):
    """Transaction status used to ensure transaction lifetime."""

    running = "running"
    rolledback = "rolledback"
    committed = "committed"
    closed = "closed"


TRepositories = TypeVar("TRepositories", bound=AsyncAbstractRepository[Any])


class AsyncUnitOfWorkTransaction(Generic[TRepositories]):
    uow: AsyncAbstractUnitOfWork[TRepositories]
    status: TransactionStatus

    def __init__(self, uow: "AsyncAbstractUnitOfWork[TRepositories]") -> None:
        self.status = TransactionStatus.running
        self.uow = uow

    def __getattr__(self, name: str) -> TRepositories:
        return getattr(self.uow, name)

    @property
    def eventstore(self) -> AsyncEventstoreAbstractRepository:
        return self.uow.eventstore

    async def commit(self) -> None:
        if self.status != TransactionStatus.running:
            raise TransactionError(f"Transaction already closed ({self.status.value}).")
        await self.uow.commit()
        self.status = TransactionStatus.committed

    async def rollback(self) -> None:
        await self.uow.rollback()
        self.status = TransactionStatus.rolledback

    async def __aenter__(self) -> AsyncUnitOfWorkTransaction[TRepositories]:
        if self.status != TransactionStatus.running:
            raise TransactionError("Invalid transaction status.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Rollback in case of exception."""
        if exc:
            await self.rollback()
            return
        if self.status == TransactionStatus.closed:
            raise TransactionError("Transaction is closed.")
        if self.status == TransactionStatus.running:
            raise TransactionError(
                "Transaction must be explicitly close. Missing commit/rollback call."
            )
        if self.status == TransactionStatus.committed:
            await self.uow.eventstore.publish_eventstream()
        self.status = TransactionStatus.closed


class AsyncAbstractUnitOfWork(abc.ABC, Generic[TRepositories]):
    """
    Abstract unit of work.

    To implement a unit of work, the :meth:`AsyncAbstractUnitOfWork.commit` and
    :meth:`AsyncAbstractUnitOfWork.rollback` has to be defined, and some repositories
    has to be declared has attributes.
    """

    eventstore: AsyncEventstoreAbstractRepository = AsyncSinkholeEventstoreRepository()

    def collect_new_events(self) -> Iterator[Message]:
        for repo in self._iter_repositories():
            while repo.seen:
                model = repo.seen.pop(0)
                while model.messages:
                    yield model.messages.pop(0)

    def _iter_repositories(
        self,
    ) -> Iterator[AsyncAbstractRepository[Any]]:
        for member_name in self.__dict__.keys():
            member = getattr(self, member_name)
            if isinstance(member, AsyncAbstractRepository):
                yield member

    async def __aenter__(self) -> AsyncUnitOfWorkTransaction[TRepositories]:
        self.__transaction = AsyncUnitOfWorkTransaction(self)
        await self.__transaction.__aenter__()
        return self.__transaction

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        # AsyncUnitOfWorkTransaction is making the thing
        await self.__transaction.__aexit__(exc_type, exc, tb)

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the transation."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rollback the transation."""
