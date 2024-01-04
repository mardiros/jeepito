from jeepito import Model
from jeepito.service._async.repository import AsyncAbstractRepository


class Dummy(Model):
    ...


class DummyRepository(AsyncAbstractRepository[Dummy]):
    ...


def test_repository_instanciate():
    repo = DummyRepository()
    assert repo.seen == []
