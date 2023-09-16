"""
Propagate commands and events to every registered handles.

"""
import logging
from typing import Any, Callable, Coroutine, TypeVar, Union

from jeepito.domain.model import Command, Event

from .service._async.unit_of_work import AsyncUnitOfWorkTransaction
from .service._sync.unit_of_work import SyncUnitOfWorkTransaction

log = logging.getLogger(__name__)

TAsyncUow = TypeVar("TAsyncUow", bound=AsyncUnitOfWorkTransaction[Any])
TSyncUow = TypeVar("TSyncUow", bound=SyncUnitOfWorkTransaction[Any])
TCommand = TypeVar("TCommand", bound=Command)
TEvent = TypeVar("TEvent", bound=Event)

AsyncCommandHandler = Callable[[TCommand, TAsyncUow], Coroutine[Any, Any, Any]]
AsyncEventHandler = Callable[[TEvent, TAsyncUow], Coroutine[Any, Any, None]]
AsyncMessageHandler = Union[
    AsyncCommandHandler[TCommand, TAsyncUow], AsyncEventHandler[TEvent, TAsyncUow]
]


SyncCommandHandler = Callable[[TCommand, TSyncUow], Any]
SyncEventHandler = Callable[[TEvent, TSyncUow], None]
SyncMessageHandler = Union[
    SyncCommandHandler[TCommand, TSyncUow], SyncEventHandler[TEvent, TSyncUow]
]
