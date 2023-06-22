"""
Repositories are used to fetch and store domain models.

Anstract repositories derived the :class:`messagebus.AsyncAbstractRepository`
class to declare every models interface such as CRUD operations,
and then concrete models implements those abstract methods for a given
storage.
"""
import abc
from typing import Generic, MutableSequence, TypeVar

from messagebus.domain.model import Model

TModel_contra = TypeVar("TModel_contra", bound=Model, contravariant=True)


class SyncAbstractRepository(abc.ABC, Generic[TModel_contra]):
    """Abstract Base Classe for Repository pattern."""

    seen: MutableSequence[TModel_contra]

    def initialize(self) -> None:
        """Override to initialize the repository (asynchronous usage)."""
