Unit Of Work using SQLAlchemy
=============================

Now that we have a finally modelized our application, we can start
storing data in a storage backend.
For the example, we will use the latestest version of SQLAlchemy, which 
is SQLAlchemy 2 at the moment.

We will use sqlite in memory for testing purpose.

::

    poetry add sqlalchemy aiosqlite


Create the sql schema
---------------------

Actually, we are not going to use `SQLAlchemy ORM`_, because we are going
to map our models directly, and because we don't needs layers of abstraction,
only the `SQLAlchemy Core`_ is enough for our use case.

The repository pattern will implement the traditional ORM part that you usually use,
but as a primary goals, we don't wan't any database implementation details in our
core domaine model, this is why we don't use SQLAlchemy ORM at all.

We will create all this code in an ``adapters`` (see :term:`Adapter`),
and create a submodul ``uow_sqla``

::

    mkdir -p src/reading_club/adapters/uow_sqla
    touch src/reading_club/adapters/__init__.py
    touch src/reading_club/adapters/uow_sqla/__init__.py
    touch src/reading_club/adapters/uow_sqla/orm.py
    touch src/reading_club/adapters/uow_sqla/uow.py

Lets create our sql schema now.

In the ``reading_club.adapters.uow_sqla.orm`` module, we will create the database
schema using the `SQLAlchemy Core`_:

.. literalinclude:: 08_sqlalchemy_uow_01.py

We will see how we map that later, before continue, lets write some
tests for our unit of work.

.. _`SQLAlchemy ORM`: https://docs.sqlalchemy.org/en/20/orm/
.. _`SQLAlchemy Core`: https://docs.sqlalchemy.org/en/20/core/ 


.. note::

    I avoid the stub of ``reading_club.adapters.uow_sqla.uow`` for the moment,
    we will get the proper implementation after the tests in order to get this
    page shorter.

Testing the unit of work
------------------------

First, We are going to separate our sql tests from others tests,
in order to get a conftest that override the ``tests/conftest.py``
but we also ensure to not use sql in the rest of the tests.
Then, we have to implement the :meth:`messagebus.AsyncAbstractUnitOfWork.commit`
and :meth:`messagebus.AsyncAbstractUnitOfWork.rollback` and we have to write transaction
tests to ensure it works.

::

    mkdir tests/uow_sqla
    touch tests/uow_sqla/__init__.py
    touch tests/uow_sqla/conftest.py
    touch tests/uow_sqla/test_transaction.py


The tests needs some sql fixture from ``uow_sqla/conftest.py``::

.. literalinclude:: 08_sqlalchemy_uow_02.py

we have an engine to bind an in memory database containing our schema, and that
can be passed to the Unit Of Work, and a session, to retrieve data from the database,
in order to get some expectation.

Now, lets write the tests in ``uow_sqla/test_transaction.py``::

.. literalinclude:: 08_sqlalchemy_uow_03.py

Both tests are really similar, they insert a book, using the uow sql connection,
in the books table, when we commit, we ensure the book is stored, when we rollback,
we ensure the book is not present.

Now that we have all we need, we can starts our implementation.


Create the sql unit of work
---------------------------

In the ``reading_club.adapters.uow_sqla.uow`` module, we will start writing
our unit of work.

.. literalinclude:: 08_sqlalchemy_uow_04.py

We have implement our unit of work and declare all our repositories without implementing
them. We explicitly raise NotImplementedError to get our repositories instanciable.

If we run our tests now:

::

    $ poetry run pytest -sxv
    ... 
    tests/test_service_handler_add_book.py::test_register_book PASSED
    tests/test_service_handler_add_book.py::test_bus_handler PASSED
    tests/uow_sqla/test_transaction.py::test_commit PASSED
    tests/uow_sqla/test_transaction.py::test_rollback PASSED
