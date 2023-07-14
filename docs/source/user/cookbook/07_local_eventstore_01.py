from typing import MutableSequence

from messagebus import AsyncEventstoreAbstractRepository, Message


class InMemoryEventstoreRepository(AsyncEventstoreAbstractRepository):
    messages: MutableSequence[Message] = []

    async def _add(self, message: Message) -> None:
        self.messages.append(message)
