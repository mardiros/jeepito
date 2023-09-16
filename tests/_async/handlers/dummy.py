from typing import Any

from jeepito.service._async.registry import async_listen
from jeepito.service._async.unit_of_work import AsyncAbstractUnitOfWork
from tests._async.conftest import DummyCommand, DummyEvent


@async_listen
async def handler(command: DummyCommand, uow: AsyncAbstractUnitOfWork[Any]):
    ...


@async_listen
async def handler_evt1(command: DummyEvent, uow: AsyncAbstractUnitOfWork[Any]):
    ...


@async_listen
async def handler_evt2(command: DummyEvent, uow: AsyncAbstractUnitOfWork[Any]):
    ...
