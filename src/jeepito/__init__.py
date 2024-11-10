"""
Jeepito API.
"""

try:
    # add an ignore for python 3.7 which does not know this standard library
    from importlib.metadata import version  # type: ignore
except ImportError:  # coverage: ignore
    from pkg_resources import get_distribution  # type: ignore

    # pythond 3.7 fallback
    def version(distribution_name: str) -> str:
        return get_distribution(distribution_name).version


from pydantic import Field

from .domain.model import (
    Command,
    Event,
    GenericCommand,
    GenericEvent,
    GenericModel,
    Message,
    Metadata,
    Model,
)
from .service._async.eventstream import (
    AsyncAbstractEventstreamTransport,
    AsyncEventstreamPublisher,
    AsyncSinkholeEventstreamTransport,
)
from .service._async.registry import AsyncMessageBus, async_listen
from .service._async.repository import AsyncAbstractRepository
from .service._async.unit_of_work import (
    AsyncAbstractUnitOfWork,
    AsyncEventstoreAbstractRepository,
    AsyncSinkholeEventstoreRepository,
    AsyncUnitOfWorkTransaction,
)
from .service._sync.eventstream import (
    SyncAbstractEventstreamTransport,
    SyncEventstreamPublisher,
    SyncSinkholeEventstreamTransport,
)
from .service._sync.registry import SyncMessageBus, sync_listen
from .service._sync.repository import SyncAbstractRepository
from .service._sync.unit_of_work import (
    SyncAbstractUnitOfWork,
    SyncEventstoreAbstractRepository,
    SyncSinkholeEventstoreRepository,
    SyncUnitOfWorkTransaction,
)
from .service.eventstream import AbstractMessageSerializer

__version__ = version("Jeepito")

__all__ = [
    # models
    "GenericCommand",
    "GenericEvent",
    "GenericModel",
    "Model",
    "Field",
    "Message",
    "Metadata",
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
    "AsyncEventstoreAbstractRepository",
    "SyncEventstoreAbstractRepository",
    "AsyncSinkholeEventstoreRepository",
    "SyncSinkholeEventstoreRepository",
    # Registry
    "async_listen",
    "sync_listen",
    "AsyncMessageBus",
    "SyncMessageBus",
    # Eventstream
    "AbstractMessageSerializer",
    "AsyncAbstractEventstreamTransport",
    "AsyncSinkholeEventstreamTransport",
    "AsyncEventstreamPublisher",
    "SyncAbstractEventstreamTransport",
    "SyncSinkholeEventstreamTransport",
    "SyncEventstreamPublisher",
]
