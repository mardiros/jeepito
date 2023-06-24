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
:class:`messagebus.Message` that are handled by the messagebus to notify
service handlers that subscribe to the events.
