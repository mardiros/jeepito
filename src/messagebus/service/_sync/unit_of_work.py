"""Unit of work"""
from __future__ import annotations

import abc
from types import TracebackType
from typing import Any, Generic, Iterator, Optional, Type

from messagebus.domain.model import Message
from messagebus.service._sync.repository import (
    SyncAbstractRepository,
    SyncEventstoreAbstractRepository,
    SyncSinkholeEventstoreRepository,
)

from ..unit_of_work import TransactionError, TransactionStatus, TRepositories


class SyncUnitOfWorkTransaction(Generic[TRepositories]):
    uow: SyncAbstractUnitOfWork[TRepositories]
    status: TransactionStatus

    def __init__(self, uow: "SyncAbstractUnitOfWork[TRepositories]") -> None:
        self.status = TransactionStatus.running
        self.uow = uow

    def __getattr__(self, name: str) -> TRepositories:
        return getattr(self.uow, name)

    def commit(self) -> None:
        self.uow.commit()
        self.status = TransactionStatus.committed

    def rollback(self) -> None:
        """Rollback the transation."""
        self.uow.rollback()
        self.status = TransactionStatus.rolledback

    def __enter__(self) -> SyncUnitOfWorkTransaction[TRepositories]:
        if self.status != TransactionStatus.running:
            raise ValueError("Invalid transaction status")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Rollback in case of exception."""
        if exc:
            self.rollback()
            return
        if self.status == TransactionStatus.closed:
            raise TransactionError("Transaction is closed")
        if self.status == TransactionStatus.running:
            raise TransactionError("Transaction must be commited or aborted")
        if self.status == TransactionStatus.committed:
            self.uow.eventstore.publish_eventstream()
        self.status = TransactionStatus.closed


class SyncAbstractUnitOfWork(abc.ABC, Generic[TRepositories]):
    eventstore: SyncEventstoreAbstractRepository = SyncSinkholeEventstoreRepository()

    def collect_new_events(self) -> Iterator[Message]:
        for repo in self._iter_repositories():
            while repo.seen:
                model = repo.seen.pop(0)
                while model.messages:
                    yield model.messages.pop(0)

    def initialize(self) -> None:
        """Initialize every repositories."""
        for repo in self._iter_repositories():
            repo.initialize()

    @classmethod
    def _iter_repositories(
        cls,
    ) -> Iterator[SyncAbstractRepository[Any]]:
        for member_name in cls.__dict__.keys():
            member = getattr(cls, member_name)
            if isinstance(member, SyncAbstractRepository):
                yield member

    def __enter__(self) -> SyncUnitOfWorkTransaction[TRepositories]:
        self.tuow = SyncUnitOfWorkTransaction(self)
        self.tuow.__enter__()
        return self.tuow

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        # AsyncUnitOfWorkTransaction is making the thing
        self.tuow.__exit__(exc_type, exc, tb)

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transation."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the transation."""
