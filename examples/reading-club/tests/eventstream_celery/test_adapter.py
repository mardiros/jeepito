import json

from lastuuid.dummies import uuidgen
from reading_club.domain.messages import RegisterBook


async def test_eventstream(uow, bus, celery_queue):
    async with uow as transaction:
        await bus.handle(
            RegisterBook(
                id=uuidgen(1),
                title="Architecture Patterns With Python",
                author="Harry Percival and Bob Gregory",
                isbn="978-1492052203",
            ),
            transaction,
        )
        await transaction.commit()

    assert len(celery_queue) > 0

    message = celery_queue[0][1]["message"]
    message["payload"] = json.loads(message["payload"])
    assert celery_queue == [
        (
            "send_message",
            {
                "message": {
                    "created_at": message["created_at"],
                    "id": str(message["id"]),
                    "payload": {
                        "id": str(uuidgen(1)),
                        "isbn": "978-1492052203",
                        "title": "Architecture Patterns With Python",
                        "author": "Harry Percival and Bob Gregory",
                    },
                    "type": "book_registered_v1",
                }
            },
        ),
    ]
