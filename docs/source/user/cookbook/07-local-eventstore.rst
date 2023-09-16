Local event store
=================

Usually, an event store centralize all the message published by many services.

An eventstore has a backend that subscribe all services eventstream and store them
in a database in order to replay them.
The local event store, I don't know if the event source world has a better name for it,
is all the message that the bus handle. event the non ``published`` flagged ones.

The message bus can store them in an event repository, usually a sql table in a
sql based repository.

For the moment, we will replace the default repository (
:class:`jeepito.AsyncSinkholeEventstoreRepository` in previous chapter)
and write our own one that store them in memory.

An ``EventstoreRepository`` is a :term:`repository` for all the local events,
its override the :class:`jeepito.AsyncEventstoreAbstractRepository`.
Only the abstract method :meth:`jeepito.AsyncEventstoreAbstractRepository._add`
needs to be implemented.


Lets just add this in our ``conftest.py`` file in order to get an eventstore.

.. literalinclude:: 07_local_eventstore_01.py


Now we can update our :term:`Unit Of Work` in order to use our eventstore implementation.

.. literalinclude:: 07_local_eventstore_02.py

Finally, we can update the tests to ensure that the message is stored.

.. literalinclude:: 07_local_eventstore_03.py

Note that there is now way to retrieve message from a
:class:`jeepito.AsyncEventstoreAbstractRepository`.
The repository is made to be a write only interface. This is why,
while testing, we add a ``# type: ignore`` by reading from our implementation detail.

Running the tests show that the eventstore is filled out by the bus.

::

    $ poetry run pytest -sxv
    ...
    collected 2 items

    tests/test_service_handler_add_book.py::test_register_book PASSED
    tests/test_service_handler_add_book.py::test_bus_handler PASSED

.. important::

    In the real world, we don't tests that a ``InMemoryUnitOfWork`` keep messages,
    it has been done here has an example. The jeepito is responsible of that
    part, nothing more.

    By the way, what has to be is the real EventstoreRepository._add method that
    received all kind of messages.

All the basics of the jeepito has been introduced, so, for now, we will create
a sql implementation of our repository to get a real storage backend example. 
