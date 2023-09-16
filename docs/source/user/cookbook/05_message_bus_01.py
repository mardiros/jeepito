from typing import Any

import pytest

from jeepito import AsyncMessageBus

# ... previous content not repeated here


# for performance reason, we reuse the bus here,
# the scan operation is slowing down while repeated
_bus: AsyncMessageBus[Any] = AsyncMessageBus()
_bus.scan("reading_club.service.handlers")


@pytest.fixture
def bus() -> AsyncMessageBus[Any]:
    return _bus
