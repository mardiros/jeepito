import asyncio
import json

from reading_club.domain.messages import RegisterBook


async def test_eventstream(uow, bus, celery_app, celery_worker):
    messages = []

    @celery_app.task(name="send_message")
    def send_message(message):
        return messages.append(message)

    celery_worker.reload()

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

    # let the worker process the task
    for _ in range(10):
        if len(messages) != 0:
            break
        await asyncio.sleep(0.1)

    assert len(messages) > 0
    for message in messages:
        message["payload"] = json.loads(message["payload"])
    assert messages == [
        {
            "created_at": messages[0]["created_at"],
            "id": messages[0]["id"],
            "payload": {
                "id": "y",
                "isbn": "978-1492052203",
                "title": "Architecture Patterns With Python",
                "author": "Harry Percival and Bob Gregory",
            },
            "type": "book_registered_v1",
        },
    ]
