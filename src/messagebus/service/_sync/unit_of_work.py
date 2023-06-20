"""Unit of work"""
from __future__ import annotations

import abc
from types import TracebackType
from typing import Iterator, Optional, Type

from messagebus.domain.model import Message
from messagebus.service._sync.repository import SyncAbstractRepository


class SyncAbstractUnitOfWork(abc.ABC):
    def collect_new_events(self) -> Iterator[Message]:
        for repo in self._iter_repositories():
            while repo.messages:
                yield repo.messages.pop(0)

    def initialize(self) -> None:
        """Initialize every repositories."""
        for repo in self._iter_repositories():
            repo.initialize()

    @classmethod
    def _iter_repositories(
        cls,
    ) -> Iterator[SyncAbstractRepository]:
        for member_name in cls.__dict__.keys():
            member = getattr(cls, member_name)
            if isinstance(member, SyncAbstractRepository):
                yield member

    def __enter__(self) -> SyncAbstractUnitOfWork:
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

    @abc.abstractmethod
    def commit(self) -> None:
        """Commit the transation."""

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollback the transation."""
