"""
messagebus API.
"""

from importlib.metadata import version

from .domain.model import Command, Event, Message, Metadata, Model
from .service._async.eventstream import (
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
)
from .service._async.registry import AsyncMessageRegistry, async_listen
from .service._async.repository import AsyncAbstractRepository
from .service._async.unit_of_work import (
    AsyncAbstractUnitOfWork,
    AsyncUnitOfWorkTransaction,
)
from .service._sync.eventstream import (
    SyncAbstractEventstreamTransport,
    SyncEventstreamPublisher,
)
from .service._sync.registry import SyncMessageRegistry, sync_listen
from .service._sync.repository import SyncAbstractRepository
from .service._sync.unit_of_work import (
    SyncAbstractUnitOfWork,
    SyncUnitOfWorkTransaction,
)
from .service.eventstream import AbstractMessageSerializer
from .service.registry import scan

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
    "AsyncUnitOfWorkTransaction",
    "SyncAbstractUnitOfWork",
    "SyncUnitOfWorkTransaction",
    # Registry
    "scan",
    "async_listen",
    "sync_listen",
    "AsyncMessageRegistry",
    "SyncMessageRegistry",
    # Eventstream
    "AbstractMessageSerializer",
    "AsyncAbstractEventstreamTransport",
    "AsyncEventstreamPublisher",
    "SyncAbstractEventstreamTransport",
    "SyncEventstreamPublisher",
]
