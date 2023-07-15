Unit Of Work
============

Now that we have a repository, and can define the unit of work for our first repository. 

.. literalinclude:: 03_unit_of_work_01.py


Thas was fast !

The unit of work methods are defined in the parent class ``AsyncAbstractUnitOfWork``.

The unit of work in here to define a business transaction. It store models and message
to process by the message bus.


Implementing a unit of work
---------------------------


As test driven developper, our, first implementation of the unit of work is written
in our``tests/conftest.py``, we have to implment the commit and rollback methods,
and, for testing purpose, we don't need to implement real transaction.

.. literalinclude:: 03_unit_of_work_02.py
