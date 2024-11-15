from messagebus import Model
from messagebus.service._sync.repository import SyncAbstractRepository


class Dummy(Model): ...


class DummyRepository(SyncAbstractRepository[Dummy]): ...


def test_repository_instanciate():
    repo = DummyRepository()
    assert repo.seen == []
