"""
messagebus is a library to send message in a bus in order to get base classes
for event driven development and domain driven development.

"""
from importlib.metadata import version
from .domain.model import Command, Event, Message, Metadata, Model
from .service._async.registry import AsyncMessageRegistry
from .service._async.repository import AsyncAbstractRepository
from .service._async.unit_of_work import AsyncAbstractUnitOfWork

from .service._sync.registry import SyncMessageRegistry
from .service._sync.repository import SyncAbstractRepository
from .service._sync.unit_of_work import SyncAbstractUnitOfWork

__version__ = version("messagebus")

__all__ = [
    "Command",
    "Event",
    "Message",
    "Metadata",
    "Model",
    "AsyncMessageRegistry",
    "AsyncAbstractRepository",
    "AsyncAbstractUnitOfWork",
    "SyncMessageRegistry",
    "SyncAbstractRepository",
    "SyncAbstractUnitOfWork",
]
