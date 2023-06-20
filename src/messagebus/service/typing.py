"""
Propagate commands and events to every registered handles.

"""
import logging
from typing import Any, Callable, Coroutine, TypeVar, Union

from messagebus.domain.model import Command, Event

from ._async.unit_of_work import AsyncAbstractUnitOfWork
from ._sync.unit_of_work import SyncAbstractUnitOfWork

log = logging.getLogger(__name__)

TCommand = TypeVar("TCommand", bound=Command)
TEvent = TypeVar("TEvent", bound=Event)

AsyncCommandHandler = Callable[
    [TCommand, AsyncAbstractUnitOfWork], Coroutine[Any, Any, Any]
]
AsyncEventHandler = Callable[
    [TEvent, AsyncAbstractUnitOfWork], Coroutine[Any, Any, None]
]
AsyncMessageHandler = Union[AsyncCommandHandler[TCommand], AsyncEventHandler[TEvent]]


SyncCommandHandler = Callable[[TCommand, SyncAbstractUnitOfWork], Any]
SyncEventHandler = Callable[[TEvent, SyncAbstractUnitOfWork], None]
SyncMessageHandler = Union[SyncCommandHandler[TCommand], SyncEventHandler[TEvent]]
