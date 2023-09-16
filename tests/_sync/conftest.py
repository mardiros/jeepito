import enum
from typing import (
    Any,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Type,
    Union,
)

import pytest
from pydantic import Field
from result import Err, Ok, Result

from jeepito.domain.model import Command, Event, Message, Metadata, Model
from jeepito.service._sync.eventstream import (
    SyncAbstractEventstreamTransport,
    SyncEventstreamPublisher,
)
from jeepito.service._sync.registry import SyncMessageBus
from jeepito.service._sync.repository import (
    SyncAbstractRepository,
    SyncEventstoreAbstractRepository,
)
from jeepito.service._sync.unit_of_work import (
    SyncAbstractUnitOfWork,
    SyncUnitOfWorkTransaction,
)

try:
    # does not exists in python 3.7
    from types import EllipsisType  # type:ignore
except ImportError:
    EllipsisType = Any  # type:ignore


class DummyError(enum.Enum):
    integrity_error = "integrity_error"
    not_found = "not_found"


class DummyModel(Model):
    id: str = Field()
    counter: int = Field(0)


DummyRepositoryOperationResult = Result[EllipsisType, DummyError]
DummyRepositoryResult = Result[DummyModel, DummyError]


class SyncDummyRepository(SyncAbstractRepository[DummyModel]):
    models: MutableMapping[str, DummyModel]

    def __init__(self) -> None:
        self.seen = []
        self.models = {}

    def add(self, model: DummyModel) -> DummyRepositoryOperationResult:
        if model.id in self.models:
            return Err(DummyError.integrity_error)
        self.models[model.id] = model
        self.seen.append(model)
        return Ok(...)

    def get(self, id: str) -> DummyRepositoryResult:
        try:
            return Ok(self.models[id])
        except KeyError:
            return Err(DummyError.not_found)


class SyncFooRepository(SyncDummyRepository):
    ...


Repositories = Union[SyncDummyRepository, SyncFooRepository]


class SyncDummyUnitOfWork(SyncAbstractUnitOfWork[Repositories]):
    def __init__(self) -> None:
        super().__init__()
        self.status = "init"
        self.foos = SyncFooRepository()
        self.bars = SyncDummyRepository()

    def commit(self) -> None:
        self.status = "committed"

    def rollback(self) -> None:
        self.status = "aborted"


class SyncEventstreamTransport(SyncAbstractEventstreamTransport):
    events: MutableSequence[Mapping[str, Any]]

    def __init__(self):
        self.events = []

    def send_message_serialized(self, message: Mapping[str, Any]) -> None:
        self.events.append(message)


class SyncDummyEventStore(SyncEventstoreAbstractRepository):
    messages: MutableSequence[Message]

    def __init__(self, publisher: Optional[SyncEventstreamPublisher]):
        super().__init__(publisher=publisher)
        self.messages = []

    def _add(self, message: Message) -> None:
        self.messages.append(message)


class SyncDummyUnitOfWorkWithEvents(SyncAbstractUnitOfWork[Repositories]):
    def __init__(self, publisher: Optional[SyncEventstreamPublisher]) -> None:
        self.foos = SyncFooRepository()
        self.bars = SyncDummyRepository()
        self.eventstore = SyncDummyEventStore(publisher=publisher)

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


class DummyCommand(Command):
    id: str = Field(...)
    metadata: Metadata = Metadata(name="dummy", schema_version=1)


class DummyEvent(Event):
    id: str = Field(...)
    increment: int = Field(...)
    metadata: Metadata = Metadata(name="dummied", schema_version=1, published=True)


@pytest.fixture
def foo_factory() -> Type[DummyModel]:
    return DummyModel


@pytest.fixture
def uow() -> Iterator[SyncDummyUnitOfWork]:
    uow = SyncDummyUnitOfWork()
    yield uow
    uow.foos.models.clear()
    uow.foos.seen.clear()
    uow.bars.models.clear()
    uow.bars.seen.clear()


@pytest.fixture
def tuow(
    uow: SyncDummyUnitOfWork,
) -> Iterator[SyncUnitOfWorkTransaction[Repositories]]:
    with uow as tuow:
        yield tuow
        tuow.rollback()


@pytest.fixture
def eventstream_transport() -> SyncEventstreamTransport:
    return SyncEventstreamTransport()


@pytest.fixture
def eventstream_pub(
    eventstream_transport: SyncEventstreamTransport,
) -> SyncEventstreamPublisher:
    return SyncEventstreamPublisher(eventstream_transport)


@pytest.fixture
def eventstore(
    eventstream_pub: SyncEventstreamPublisher,
) -> SyncDummyEventStore:
    return SyncDummyEventStore(eventstream_pub)


@pytest.fixture
def uow_with_eventstore(
    eventstream_pub: SyncEventstreamPublisher,
) -> Iterator[SyncDummyUnitOfWorkWithEvents]:
    uow = SyncDummyUnitOfWorkWithEvents(eventstream_pub)
    yield uow
    uow.eventstore.messages.clear()  # type: ignore
    uow.foos.models.clear()
    uow.foos.seen.clear()
    uow.bars.models.clear()
    uow.bars.seen.clear()


@pytest.fixture
def bus() -> SyncMessageBus[Repositories]:
    return SyncMessageBus()


@pytest.fixture
def dummy_command() -> DummyCommand:
    return DummyCommand(id="dummy_cmd")


@pytest.fixture
def dummy_event() -> DummyEvent:
    return DummyEvent(id="dummy_evt", increment=1)
