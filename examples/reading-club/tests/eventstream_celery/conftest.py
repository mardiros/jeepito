from collections.abc import Mapping, MutableSequence
from typing import Any

import pytest
from reading_club.adapters.eventstream import EventstreamTransport

from jeepito import AsyncAbstractEventstreamTransport


class FakeCelery:
    def __init__(self, queue: MutableSequence[Any]) -> None:
        self.queue = queue

    def send_task(self, task: str, kwargs: Mapping[str, Any]) -> None:
        self.queue.append((task, kwargs))


@pytest.fixture
def celery_queue() -> MutableSequence[Any]:
    return []


@pytest.fixture
def celery_app(celery_queue) -> FakeCelery:
    return FakeCelery(celery_queue)


@pytest.fixture
def transport(celery_app) -> AsyncAbstractEventstreamTransport:
    return EventstreamTransport(celery_app)
