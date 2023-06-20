"""
Repositories are used to fetch and store domain models.

Anstract repositories derived the :class:`messagebus.AsyncAbstractRepository`
class to declare every models interface such as CRUD operations,
and then concrete models implements those abstract methods for a given
storage.
"""
import abc
from typing import MutableSequence

from messagebus.domain.model import Message


class SyncAbstractRepository(abc.ABC):
    """Abstract Base Classe for Repository pattern."""

    messages: MutableSequence[Message]
    """
    List of messages consumed by the unit of work to mutate the repository.

    Those message are ephemeral, published by event handler and consumed
    by the unit of work during the process of an original command.
    """

    def initialize(self) -> None:
        """Override to initialize the repository (asynchronous usage)."""
