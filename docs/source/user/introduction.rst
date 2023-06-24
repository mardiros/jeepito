Introduction
============

messagebus is a library that implement some :term:`Domain Driven Design`
approach that is popularised by the book :term:`Architecture Patterns With Python`.

It encourage to create a domain model, by subclassing the class
:class:`messagebus.Model`, and by writing :class:`messagebus.Command` and
:class:`messagebus.Event`.


:class:`messagebus.Model` are stored and accessed via repositories.
Every models has its own :term:`repository`, a subclass of 
:class:`messagebus.AsyncAbstractRepository` and those repositories
are then gather in a :term:`Unit Of Work`.

Mutations of the models are also part of the domain models, those mutations are
store in specific objects, named :term:`Command` and :term:`Event`.

Commands are implemented by subclassing the :class:`messagebus.Command`
in order to discribe the intention of the mutation.

Events are implemented by subclassing the :class:`messagebus.Event`
in order to discribe that the mutation has happened.

Commands and events are versionned, the update of any format, that represent a
:term:`Breaking Change` is discouraged without creating a new version.

:class:`messagebus.Command` and :class:`messagebus.Event` are both
:class:`messagebus.Message`. And those messages can be listened by a
:term:`service handler`, in a :class:`messagebus.AsyncMessageRegistry`
using a decorator :func:`messagebus.async_listen`.

.. note::
    The :class:`messagebus.SyncMessageRegistry` has to be used with the
    decorator :func:`messagebus.sync_listen` for the synchronous version.

During the startup of the app, all service handlers must be registered
the message registry by calling the function :func:`messagebus.scan`.

Afterwhat, the :class:`messagebus.AsyncMessageRegistry` is ready to handle
message using it function :meth:`messagebus.AsyncMessageRegistry.handle`.
you will have understood it, the :class:`messagebus.AsyncMessageRegistry`
is the :term:`message bus` object.

Finally, when the unit of work commit its transaction, the a publisher
object can send all the desired message to an :term:`Event Stream`.

This is a bit condensed, but the essence of the event driven throw the
message bus, is here. So lets get deeper going step by step.