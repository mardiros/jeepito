Service Handler
===============

A service handler is a method that receive a command and process it in the unit of work.


Here is the signature:

.. literalinclude:: 04_service_handler_01.py

.. important::

    At this time, this is the first line of code we are going to write that are
    representing an implementation. This implementation is based on abstract object,
    so it does not care of implementation details.

Before implementing the service, we will write the testing part.

In the file ``test_service_handler_add_book.py``

.. literalinclude:: 04_service_handler_02.py

we have imagine a tests where we ensure we can add the book in the repository
properly, and then, that the book cannot be added twice due to an integrity error.

This should be splitted in two tests but this is not a test driven course here,
and we can live with that at the moment. We will do that later.

The tests requires pytest fixtures, so we been to update our ``conftest.py`` now.

Lets write our fixtures:

.. literalinclude:: 04_service_handler_03.py
   :emphasize-lines: 47,57

We have two fixtures here, ``register_book_cmd`` is a dummy command to register a book,
using a fixture instead of hardcoding it in the test make it reusable and make the test
clear on its assertion. Using command as fixture can also be reused by other fixtures
in order to initialize a domain model state using service handlers, and it avoid update
if the core domain model has been updated.
The ``uow`` fixture is our reusable unit of work, which run in memory, so we don't have
hard dependency on any SQL Engine. This add more code to maintaine, but it is highly
flexible code. Not taht its states is cleared avec every tests in order to make sure
every tests are decoupled.

We are ready to starts our test:

::

    =============================== FAILURES ================================
    __________________________ test_register_book ___________________________

    register_book_cmd = RegisterBook(message_id='13e01ffe-1363-11ee-be97-5c80b62b9562', created_at=datetime.datetime(2023, 6, 25, 14, 17, 55, ...', schema_version=1, published=False), id='x', isbn='0-321-12521-5', title='Domain Driven Design', author='Eric Evans')
    uow = <tests.conftest.InMemoryUnitOfWork object at 0x7fb413010710>

        async def test_register_book(register_book_cmd: RegisterBook, uow: AbstractUnitOfWork):
            async with uow as transaction:
    >           operation = await register_book(register_book_cmd, transaction)

    tests/test_service_handler_add_book.py:10:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    cmd = RegisterBook(message_id='13e01ffe-1363-11ee-be97-5c80b62b9562', created_at=datetime.datetime(2023, 6, 25, 14, 17, 55, ...', schema_version=1, published=False), id='x', isbn='0-321-12521-5', title='Domain Driven Design', author='Eric Evans')
    uow = <jeepito.service._async.unit_of_work.AsyncUnitOfWorkTransaction object at 0x7fb413010b10>

        async def register_book(
            cmd: RegisterBook, uow: AsyncUnitOfWorkTransaction
        ) -> BookRepositoryOperationResult:
    >       raise NotImplementedError
    E       NotImplementedError

    src/reading_club/service/handlers/book.py:11: NotImplementedError
    ======================== short test summary info ========================



Now, that our tests is working, and properly failing, we can implement our service handler:

.. literalinclude:: 04_service_handler_04.py
   :emphasize-lines: 11-13

::

    $poetry run pytest -v
    ========================== test session starts ==========================
    collected 1 item

    tests/test_service_handler_add_book.py::test_register_book PASSED [100%]

    =========================== 1 passed in 0.01s ===========================


.. note::

    If you are not used to hexagonal architecture, you may be surprise by the code
    quantity written for testing purpose.

    The big plus here is how maintainable is this code, we don't have any mocks, so
    we don't tests signature of object called, we can refactor and rely on our tests
    with more confidence.

    By the way, those code are not that much hard to write and maintain, I personnaly
    find the fixture part, one of the funniest part to code.
