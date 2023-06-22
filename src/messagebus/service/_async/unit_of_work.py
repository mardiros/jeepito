"""Unit of work"""
from __future__ import annotations

import abc
from types import TracebackType
from typing import Any, Iterator, Optional, Type

from typing_extensions import Self

from messagebus.domain.model import Message
from messagebus.service._async.repository import AsyncAbstractRepository


class AsyncAbstractUnitOfWork(abc.ABC):
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

    async def __aenter__(self) -> Self:
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

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the transation."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rollback the transation."""
