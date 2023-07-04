Message Bus
===========

Now that we have a service handler, it is time to handle it via the message bus.

Let starts by implementing a fixture in the ``conftest.py``

.. literalinclude:: 05_message_bus_01.py

And a tests that use the bus of message to handler the command.

.. literalinclude:: 05_message_bus_02.py


Lets run the test to see what happen.


::

    $ poetry run pytest -sxv
    ...
    tests/test_service_handler_add_book.py::test_bus_handler FAILED

    =============================== FAILURES ================================
    ___________________________ test_bus_handler ____________________________

    bus = <messagebus.service._async.registry.AsyncMessageBus object at 0x7f27b2c07810>
    register_book_cmd = RegisterBook(message_id='6cff6902-139d-11ee-b0cb-5c80b62b9562', created_at=datetime.datetime(2023, 6, 25, 21, 15, 35, ...', schema_version=1, published=False), id='x', isbn='0-321-12521-5', title='Domain Driven Design', author='Eric Evans')
    uow = <tests.conftest.InMemoryUnitOfWork object at 0x7f27b2c7b650>

        async def test_bus_handler(
            bus: AsyncMessageBus, register_book_cmd: RegisterBook, uow: AbstractUnitOfWork
        ):
            async with uow as trans:
                await bus.handle(register_book_cmd, trans)
                book = await trans.books.by_id(register_book_cmd.id)
    >           assert book.is_ok()
    E           AssertionError: assert False
    E            +  where False = <bound method Err.is_ok of Err(<BookRepositoryError.not_found: 'not_found'>)>()
    E            +    where <bound method Err.is_ok of Err(<BookRepositoryError.not_found: 'not_found'>)> = Err(<BookRepositoryError.not_found: 'not_found'>).is_ok

    tests/test_service_handler_add_book.py:37: AssertionError
    ======================== short test summary info ========================
    FAILED tests/test_service_handler_add_book.py::test_bus_handler - AssertionError: assert False
    !!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!


The tests has failed because we did dot hook the ``@async_listen`` decorator,
so, when we scan the message, the message bus did not add the function to its registry of service handler.

Lets fix the service/handlers/book.py file

.. literalinclude:: 05_message_bus_03.py

::

    $ poetry run pytest -sxv
    ========================== test session starts ==========================
    collected 2 items

    tests/test_service_handler_add_book.py::test_register_book PASSED
    tests/test_service_handler_add_book.py::test_bus_handler PASSED

    =========================== 2 passed in 0.01s ===========================

Now, while handling the command, the message bus call the service handlers, and all
hook from the scanned module.
