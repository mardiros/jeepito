Introduction
============

jeepito is a library that implement some :term:`Domain Driven Design`
approach that is popularised by the book :term:`Architecture Patterns With Python`.

It encourage to create a domain model, by subclassing the class
:class:`jeepito.Model`, and by writing :class:`jeepito.Command` and
:class:`jeepito.Event`.


:class:`jeepito.Model` are stored and accessed via repositories.
Every models has its own :term:`repository`, a subclass of 
:class:`jeepito.AsyncAbstractRepository` and those repositories
are then gather in a :term:`Unit Of Work`.

Mutations of the models are also part of the domain models, those mutations are
store in specific objects, named :term:`Command` and :term:`Event`.

Commands are implemented by subclassing the :class:`jeepito.Command`
in order to discribe the intention of the mutation.

Events are implemented by subclassing the :class:`jeepito.Event`
in order to discribe that the mutation has happened.

Commands and events are versionned, the update of any format, that represent a
:term:`Breaking Change` is discouraged without creating a new version.

:class:`jeepito.Command` and :class:`jeepito.Event` are both
:class:`jeepito.Message`. And those messages can be listened by a
:term:`service handler`, in a :class:`jeepito.AsyncMessageBus`
using a decorator :func:`jeepito.async_listen`.

.. note::
    The :class:`jeepito.SyncMessageRegistry` has to be used with the
    decorator :func:`jeepito.sync_listen` for the synchronous version.

During the startup of the app, all service handlers must be registered
the message registry by calling the function :func:`jeepito.scan`.

Afterwhat, the :class:`jeepito.AsyncMessageBus` is ready to handle
message using it function :meth:`jeepito.AsyncMessageBus.handle`.
you will have understood it, the :class:`jeepito.AsyncMessageBus`
is the :term:`message bus` object.

Finally, when the unit of work commit its transaction, the a publisher
object can send all the desired message to an :term:`Event Stream`.

This is a bit condensed, but the essence of the event driven throw the
message bus, is here. So lets get deeper going step by step in the
cookbook.