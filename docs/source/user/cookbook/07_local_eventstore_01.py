from collections.abc import MutableSequence
from typing import Any, ClassVar

from jeepito import AsyncEventstoreAbstractRepository, Message


class InMemoryEventstoreRepository(AsyncEventstoreAbstractRepository):
    messages: ClassVar[MutableSequence[Message[Any]]] = []

    async def _add(self, message: Message[Any]) -> None:
        self.messages.append(message)
