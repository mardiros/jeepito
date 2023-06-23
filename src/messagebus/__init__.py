"""
messagebus API.
"""

from importlib.metadata import version

from .domain.model import Command, Event, Message, Metadata, Model
from .service._async.eventstream import (
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
)
from .service._async.registry import AsyncMessageRegistry
from .service._async.repository import AsyncAbstractRepository
from .service._async.unit_of_work import AsyncAbstractUnitOfWork
from .service._sync.eventstream import (
    SyncAbstractEventstreamTransport,
    SyncEventstreamPublisher,
)
from .service._sync.registry import SyncMessageRegistry
from .service._sync.repository import SyncAbstractRepository
from .service._sync.unit_of_work import SyncAbstractUnitOfWork
from .service.eventstream import AbstractMessageSerializer

__version__ = version("messagebus")

__all__ = [
    # models
    "Command",
    "Event",
    "Message",
    "Metadata",
    "Model",
    # Repository
    "AsyncAbstractRepository",
    "SyncAbstractRepository",
    # Unit of work
    "AsyncAbstractUnitOfWork",
    "SyncAbstractUnitOfWork",
    # Registry
    "AsyncMessageRegistry",
    "SyncMessageRegistry",
    # Eventstream
    "AbstractMessageSerializer",
    "AsyncAbstractEventstreamTransport",
    "AsyncEventstreamPublisher",
    "SyncAbstractEventstreamTransport",
    "SyncEventstreamPublisher",
]
