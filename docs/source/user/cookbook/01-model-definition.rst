Define the core model
=====================

The domain drive design approach is core domain model centric. 
The core model contains only the business logic of the app, nothing more.

Initial model
-------------

The first step is to define a model, at the moment, we don't need
to create a complete model, we can start by creating model to register
books. So let start that simple.

In a `domain/model.py` we can store the following model.

.. literalinclude:: 01_model_definition_01.py


Why there is a domain module ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In traditional apps, we use to create a ``model`` module at the root of the
project, so, it is legitimate to ask why we create a ``domain`` namespace.
The ``domain`` module contains all the business logic, and it is the namespace
where we only with the language of the business domain. In domain driven design,
it is named the :term:`Ubiquitous Language`

In a Django app, for example, the model contains database details, such as
forein keys, index and also contains some GUI details.

In the domain module, this is not the proper place for that. Says differently,
you can't use an ORM to describe your domain model.



.. note::

    Behind the scene, messagebus use pydantic, the `Field` is just a reexport of
    the pydantic Field class.


Defining commands
-----------------

In a `domain/messages.py` we define the format of model updates.

Let start by a command to create a book.

.. literalinclude:: 01_model_definition_02.py

The command field describe the data payload of the command, it represent the contract
of the command. Every update that introduce a :term:`Breaking Change` of the command
are discouraged, in that case, a new command is created with the change updated.

.. note::

    For example, if we want to transform the author by a list of authors, it is
    a breaking change, and a new version of the command has to be created. 

    .. literalinclude:: 01_model_definition_03.py
