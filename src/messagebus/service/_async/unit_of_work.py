"""Unit of work"""
from __future__ import annotations

import abc
import enum
from types import TracebackType
from typing import Any, Iterator, Optional, Type

from messagebus.domain.model import Message
from messagebus.service._async.repository import (
    AsyncAbstractRepository,
    AsyncEventstoreAbstractRepository,
    AsyncSinkholeEventstoreRepository,
)


class TransactionError(RuntimeError):
    ...


class TransactionStatus(enum.Enum):
    running = "running"
    rolledback = "rolledback"
    committed = "committed"
    closed = "closed"


class AsyncUnitOfWorkTransaction:
    uow: AsyncAbstractUnitOfWork
    status: TransactionStatus

    def __init__(self, uow: "AsyncAbstractUnitOfWork") -> None:
        self.status = TransactionStatus.running
        self.uow = uow

    def __getattr__(self, name: str) -> AsyncAbstractRepository[Any]:
        return getattr(self.uow, name)

    async def commit(self) -> None:
        await self.uow.commit()
        self.status = TransactionStatus.committed

    async def rollback(self) -> None:
        """Rollback the transation."""
        await self.uow.rollback()
        self.status = TransactionStatus.rolledback

    async def __aenter__(self) -> AsyncUnitOfWorkTransaction:
        if self.status != TransactionStatus.running:
            raise ValueError("Invalid transaction status")
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
            raise TransactionError("Transaction is closed")
        if self.status == TransactionStatus.running:
            raise TransactionError("Transaction must be commited or aborted")
        if self.status == TransactionStatus.committed:
            await self.uow.eventstore.publish_eventstream()
        self.status = TransactionStatus.closed


class AsyncAbstractUnitOfWork(abc.ABC):
    eventstore: AsyncEventstoreAbstractRepository = AsyncSinkholeEventstoreRepository()

    def collect_new_events(self) -> Iterator[Message]:
        for repo in self._iter_repositories():
            while repo.seen:
                model = repo.seen.pop(0)
                while model.messages:
                    yield model.messages.pop(0)

    async def initialize(self) -> None:
        """Initialize every repositories."""
        for repo in self._iter_repositories():
            await repo.initialize()

    @classmethod
    def _iter_repositories(
        cls,
    ) -> Iterator[AsyncAbstractRepository[Any]]:
        for member_name in cls.__dict__.keys():
            member = getattr(cls, member_name)
            if isinstance(member, AsyncAbstractRepository):
                yield member

    async def __aenter__(self) -> AsyncUnitOfWorkTransaction:
        self.tuow = AsyncUnitOfWorkTransaction(self)
        await self.tuow.__aenter__()
        return self.tuow

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        # AsyncUnitOfWorkTransaction is making the thing
        await self.tuow.__aexit__(exc_type, exc, tb)

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the transation."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rollback the transation."""
