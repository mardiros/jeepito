Repository
==========

Repository define operation to retrieve and store data from a storage backend.

While creating the application, we create definition of those methods in an
abstract class. This let the possibility to improve the testability of the application.

Lets define an operation to add a book in the ``service/repositories.py`` module.

.. literalinclude:: 02_repository_01.py


Dealing with errors
-------------------

First, we create types that describe results from the repository.
This is a personal choice to avoid exceptions here to deal with error, the messagebus
is not enforcing this kind of practice.

The ``BookRepositoryError`` describe all kind of errors the repository can encountered,
for instance, the ``add`` method can raises integrity error in case of duplicate things,
and, the ``get`` method can raises a not found error. Instead of raising exceptions,
the repository wrap the result in an object that must be unwrap to get the response
or the error.


The ``AbstractBookRepository`` inherits ``AsyncAbstractRepository`` and note that it
manage ``Book`` models. It define two operations on book, an operation to add a book
in the repository, and one operation to retrieve a book from the repository.

.. note::
    At this point, we only create definitions, this is why, there is still no tests
    written.


Implementing a repository
-------------------------

The first implementation of our repository is always the simplest one, we can create
on in a ``tests/conftest.py`` to get a better view of what it looks like.

.. literalinclude:: 02_repository_02.py


If you plan to store the models in a SQL database, the cool things is that, it
can be done later. We can crunch the model, and a complete prototype of the app,
without any sql migration noise and stay focus on the model itself.

This pattern comes from the :term:`Hexagonal Architecture`, the storage backend is
an implementation detail.
