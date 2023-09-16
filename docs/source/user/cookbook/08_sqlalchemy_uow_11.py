from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from jeepito import (
    AsyncEventstoreAbstractRepository,
    AsyncEventstreamPublisher,
    Message,
)

from . import orm


class SQLEventstoreRepository(AsyncEventstoreAbstractRepository):
    def __init__(self, session: AsyncSession, publisher: AsyncEventstreamPublisher):
        super().__init__(publisher)
        self.session = session

    async def _add(self, message: Message) -> None:
        qry = insert(orm.messages).values(
            [
                {
                    "id": message.message_id,
                    "created_at": message.created_at,
                    "metadata": message.metadata.model_dump(),
                    "payload": message.model_dump(
                        exclude={"message_id", "created_at", "metadata"}
                    ),
                }
            ]
        )
        await self.session.execute(qry)
