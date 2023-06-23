"""
Propagate commands and events to every registered handles.

"""
import logging
from typing import Any, Callable, Coroutine, TypeVar, Union

from messagebus.domain.model import Command, Event

from .service._async.unit_of_work import AsyncAbstractUnitOfWork
from .service._sync.unit_of_work import SyncAbstractUnitOfWork

log = logging.getLogger(__name__)

TSyncUow = TypeVar("TSyncUow", bound=AsyncAbstractUnitOfWork[Any])
TAsyncUow = TypeVar("TAsyncUow", bound=SyncAbstractUnitOfWork[Any])
TCommand = TypeVar("TCommand", bound=Command)
TEvent = TypeVar("TEvent", bound=Event)

AsyncCommandHandler = Callable[[TCommand, TSyncUow], Coroutine[Any, Any, Any]]
AsyncEventHandler = Callable[[TEvent, TSyncUow], Coroutine[Any, Any, None]]
AsyncMessageHandler = Union[
    AsyncCommandHandler[TCommand, TSyncUow], AsyncEventHandler[TEvent, TSyncUow]
]


SyncCommandHandler = Callable[[TCommand, TAsyncUow], Any]
SyncEventHandler = Callable[[TEvent, TAsyncUow], None]
SyncMessageHandler = Union[
    SyncCommandHandler[TCommand, TAsyncUow], SyncEventHandler[TEvent, TAsyncUow]
]
