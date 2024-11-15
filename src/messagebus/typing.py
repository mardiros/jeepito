"""
Propagate commands and events to every registered handles.

"""

import logging
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from messagebus.domain.model import Message

from .service._async.unit_of_work import AsyncAbstractUnitOfWork
from .service._sync.unit_of_work import SyncAbstractUnitOfWork

log = logging.getLogger(__name__)

TAsyncUow = TypeVar("TAsyncUow", bound=AsyncAbstractUnitOfWork[Any])
TSyncUow = TypeVar("TSyncUow", bound=SyncAbstractUnitOfWork[Any])
TMessage = TypeVar("TMessage", bound=Message[Any])

AsyncMessageHandler = Callable[[TMessage, TAsyncUow], Coroutine[Any, Any, Any]]
SyncMessageHandler = Callable[[TMessage, TSyncUow], Any]
