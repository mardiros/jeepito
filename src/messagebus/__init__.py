"""
messagebus API.
"""

from importlib.metadata import version

from pydantic import Field

from .domain.model import Command, Event, Message, Metadata, Model
from .service._async.eventstream import (
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
)
from .service._async.registry import AsyncMessageBus, async_listen
from .service._async.repository import AsyncAbstractRepository
from .service._async.unit_of_work import (
    AsyncAbstractUnitOfWork,
    AsyncUnitOfWorkTransaction,
)
from .service._sync.eventstream import (
    SyncAbstractEventstreamTransport,
    SyncEventstreamPublisher,
)
from .service._sync.registry import SyncMessageBus, sync_listen
from .service._sync.repository import SyncAbstractRepository
from .service._sync.unit_of_work import (
    SyncAbstractUnitOfWork,
    SyncUnitOfWorkTransaction,
)
from .service.eventstream import AbstractMessageSerializer

__version__ = version("messagebus")

__all__ = [
    # models
    "Model",
    "Message",
    "Metadata",
    "Model",
    "Field",
    "Command",
    "Event",
    # Repository
    "AsyncAbstractRepository",
    "SyncAbstractRepository",
    # Unit of work
    "AsyncAbstractUnitOfWork",
    "AsyncUnitOfWorkTransaction",
    "SyncAbstractUnitOfWork",
    "SyncUnitOfWorkTransaction",
    # Registry
    "async_listen",
    "sync_listen",
    "AsyncMessageBus",
    "SyncMessageBus",
    # Eventstream
    "AbstractMessageSerializer",
    "AsyncAbstractEventstreamTransport",
    "AsyncEventstreamPublisher",
    "SyncAbstractEventstreamTransport",
    "SyncEventstreamPublisher",
]
