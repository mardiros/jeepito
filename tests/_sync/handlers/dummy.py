from typing import Any

from jeepito.service._sync.registry import sync_listen
from jeepito.service._sync.unit_of_work import SyncAbstractUnitOfWork
from tests._sync.conftest import DummyCommand, DummyEvent


@sync_listen
def handler(command: DummyCommand, uow: SyncAbstractUnitOfWork[Any]): ...


@sync_listen
def handler_evt1(command: DummyEvent, uow: SyncAbstractUnitOfWork[Any]): ...


@sync_listen
def handler_evt2(command: DummyEvent, uow: SyncAbstractUnitOfWork[Any]): ...
