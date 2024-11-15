import pytest

from messagebus.domain.model import GenericEvent
from messagebus.service._sync.unit_of_work import (
    SyncUnitOfWorkTransaction,
    TransactionError,
    TransactionStatus,
)
from tests._sync.conftest import DummyModel, MyMetadata, SyncDummyUnitOfWork


class FooCreated(GenericEvent[MyMetadata]):
    id: str
    metadata: MyMetadata = MyMetadata(
        name="foo_created",
        schema_version=1,
        published=True,
        custom_field="",
    )


class BarCreated(GenericEvent[MyMetadata]):
    metadata: MyMetadata = MyMetadata(
        name="bar_created",
        schema_version=1,
        published=True,
        custom_field="",
    )


def test_collect_new_events(uow: SyncDummyUnitOfWork, foo_factory: type[DummyModel]):
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
            tuow.foos  # noqa B018

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
        transaction = SyncUnitOfWorkTransaction(uow)
        transaction.status = TransactionStatus.committed
        with transaction:
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
