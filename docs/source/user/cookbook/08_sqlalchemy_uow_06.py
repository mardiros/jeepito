import pytest
from lastuuid.dummies import uuidgen
from reading_club.adapters.uow_sqla.uow import SQLUnitOfWork
from reading_club.domain.model import Book
from sqlalchemy.ext.asyncio import AsyncEngine

from jeepito import AsyncAbstractEventstreamTransport


@pytest.fixture
def uow(
    transport: AsyncAbstractEventstreamTransport, sqla_engine: AsyncEngine
) -> SQLUnitOfWork:
    return SQLUnitOfWork(transport, sqla_engine)


@pytest.fixture
def book():
    return Book(
        id=uuidgen(1),
        title="Domain Driven Design",
        author="Eric Evans",
        isbn="0-321-12521-5",
    )
