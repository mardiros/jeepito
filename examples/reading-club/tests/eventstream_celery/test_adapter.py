import json

from reading_club.domain.messages import RegisterBook


async def test_eventstream(uow, bus, celery_queue):
    async with uow as transaction:
        await bus.handle(
            RegisterBook(
                id="y",
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
                    "id": message["id"],
                    "payload": {
                        "id": "y",
                        "isbn": "978-1492052203",
                        "title": "Architecture Patterns With Python",
                        "author": "Harry Percival and Bob Gregory",
                    },
                    "type": "book_registered_v1",
                }
            },
        ),
    ]
