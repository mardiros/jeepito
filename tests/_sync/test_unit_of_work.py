from typing import Any, Type

import pytest

from messagebus.domain.model import Event, Metadata
from messagebus.service._sync.unit_of_work import (
    SyncUnitOfWorkTransaction,
    TransactionError,
    TransactionStatus,
)
from tests._sync.conftest import SyncDummyUnitOfWork, DummyModel


class FooCreated(Event):
    id: str
    metadata: Metadata = Metadata(name="foo_created", schema_version=1, published=True)

    def __eq__(self, other: Any):
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


class BarCreated(Event):
    metadata: Metadata = Metadata(name="bar_created", schema_version=1, published=True)

    def __eq__(self, other: Any):
        slf = self.dict(exclude={"message_id", "created_at"})
        otr = other.dict(exclude={"message_id", "created_at"})
        return slf == otr


def test_collect_new_events(
    uow: SyncDummyUnitOfWork, foo_factory: Type[DummyModel]
):
    foo = foo_factory(id="1", counter=0)
    foo.messages.append(FooCreated(id="1"))
    bar = foo_factory(id="1", counter=0)
    bar.messages.append(BarCreated())
    foo2 = foo_factory(id="2", counter=0)
    foo2.messages.append(FooCreated(id="2"))

    with uow as tuow:
        tuow.foos.add(foo)
        tuow.bars.add(bar)
        tuow.foos.add(foo2)
        tuow.commit()

    iter = uow.collect_new_events()
    assert next(iter) == FooCreated(id="1")
    assert next(iter) == FooCreated(id="2")
    assert next(iter) == BarCreated()
    with pytest.raises(StopIteration):
        next(iter)


def test_transaction_rollback_on_error(uow: SyncDummyUnitOfWork):
    tuow = None
    try:
        with uow as tuow:
            raise ValueError("Boom")
    except Exception:
        ...
    assert tuow is not None
    assert tuow.status == TransactionStatus.rolledback


def test_transaction_rollback_explicit_commit(uow: SyncDummyUnitOfWork):
    with pytest.raises(TransactionError) as ctx:
        with uow as tuow:
            tuow.foos

    assert str(ctx.value).endswith(
        "Transaction must be explicitly close. Missing commit/rollback call."
    )


def test_transaction_invalid_state(uow: SyncDummyUnitOfWork):
    with pytest.raises(TransactionError) as ctx:
        with uow as tuow:
            tuow.status = TransactionStatus.closed

    assert str(ctx.value).endswith("Transaction is closed.")


def test_transaction_invalid_usage(uow: SyncDummyUnitOfWork):
    with pytest.raises(TransactionError) as ctx:
        trans = SyncUnitOfWorkTransaction(uow)
        trans.status = TransactionStatus.committed
        with trans:
            ...

    assert str(ctx.value).endswith("Invalid transaction status.")


def test_transaction_commit_after_rollback(uow: SyncDummyUnitOfWork):
    with pytest.raises(TransactionError) as ctx:
        with uow as tuow:
            tuow.rollback()
            tuow.commit()

    assert str(ctx.value).endswith("Transaction already closed (rolledback).")


def test_transaction_commit_twice(uow: SyncDummyUnitOfWork):
    with pytest.raises(TransactionError) as ctx:
        with uow as tuow:
            tuow.commit()
            tuow.commit()

    assert str(ctx.value).endswith("Transaction already closed (committed).")
