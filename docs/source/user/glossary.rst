Glossary
========

.. glossary::

   Architecture Patterns With Python

      *Architecture Patterns With Python: Enabling Test-Driven Development,
      Domain-Driven Design, and Event-Driven Microservices* is a book from
      Harry J.W. Percival and Bob Gregory that expose design pattern coming from
      :term:`DDD`. 

   Breaking Change
      In programming, updating contracts can involve breaking changes.
      Not every changes are breaker.
      Breaking changes should be well known and documented by software maintener.
      Usually, breaking changes are:

      * adding a new required field (or marking an optional field required)
      * removing required field
      * renaming field
      * removing or renaming enum values

      Non breaking changes are:

      * adding a new type of operation (api method, command, event)
      * adding an optional field
      * adding an enum value

      Those rules are used to define when a new version is required. When a new
      version of an operation is created, a new handler is created for that version,
      the old one is kept as is, or updated if necessary, reused in case of
      :term:`Event Replay`.

   casualcms
      A CMS Engine
      https://github.com/mardiros/casualcms/

   Command
      A command is an object that represent an intention of mutation of the
      :term:`Domain Model`.
      This is an atomic change. Commands are timestamped, ordered, and immutable.
      In :term:`Event Sourcing`, we store those commands as the source of truth.

   DDD
      :term:`Domain Driven Design` acronym.

   Domain Model
      In :term:`DDD`, the domain model represent the layer part of the software
      that focus on representing the structure of the business rules of the application.
      In the domain model layer, there is no implementation details involved, neither
      database storage engine, nor graphical user interface representation.

   Domain Driven Design
      A software design approach focusing on modeling software to match a domain
      according to input from that domain's experts.

      The term was coined by Eric Evans in his book of the same title published in 2003. 

      https://en.wikipedia.org/wiki/Domain-driven_design

   Event
      An event is an object that represent a mutation of the model has happened.
      Like commands, Events are timestamped, ordered and immutable.
      In :term:`Event Sourcing`, we store those events as the source of truth
      and we use an :term:`Event Stream` in order to propagate events to subscribers
      that can update or react by the reception of an event.

   Event Replay
      In the :term:`Event Sourcing` world, we replay all events from an
      :term:`Event Store` in the proper order in order to create an application state.
      We may also replay the event to a specific timestamp in order to reproduce a bug,
      or to recreate a new database schema and fill out it by replaying those events
      with appropriate event handlers.

   Event Store
      A storage backend that save all the events ordered.

   Event Sourcing
      A software development strategy based on storing model mutations instead of
      a current model state.

   Event Stream
      In software development, an event stream is a PUB/SUB component where publisher
      submit their internal changes publicaly, and subscribers react when receiving
      those events. Usually most services are publisher and subscriber, they receive
      events, they update their internal state and publish an event due to the update.

   Gandi
      A domain name registrar.
      https://www.gandi.net/

   Hexagonal Architecture
      An architectural pattern used in software design to create loosely coupled
      application components that can be easily connected. The testability of
      hexagonal application is improved by making components exchangeable on any
      level of abstraction.

      The term was coined by Alistair Cockburn in 2005.
      https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)

   Message
      A :term:`Command` or an :term:`Event`.

   Message Bus
      The bus of message is the software component that dispatch commands and events
      to handlers in order to update the :term:`Domain Model`, using
      a :term:`Unit Of Work`.

   purgatory
      A circuit breaker implementation
      https://github.com/mardiros/purgatory/

   Service Handler
      A hook function which is made to update the application state, or to react to
      a message from the bus. This hook is called by the :term:`message bus` and has
      two parameters, a :term:`Message`, and a :term:`Unit Of Work`.
      When the message is received, the service handler will update application
      state throw the Unit Of Work.
      Thus, if the message is a :term:`Command`, the service handler may return an
      object. For instance a ``CreateObject`` can return an ``Object`` created by the
      service handler.
      Finally, a Service Handler can also create sub message to process, those message
      will run inside the same transaction of the :term:`Unit Of Work`.

   Ubiquitous Language
      In the Domain Driven Design book, Eric introduce the approach by communication
      issue, where stake holder and developper does not share the same language.
      When you work as a team, we have to establish the same language for every
      team player, to get the best communication between people. The vocabulary used
      to discribe a the business and shared by all the team is named the Ubiquitous
      Language. This is the first step of the :term:`DDD`, following design patterns
      like unit of work is not enough to practice DDD.

   Unit Of Work
      The unit of work is an object which is responsible to represent a transaction
      at the business layer. The messagebus
      https://en.wikipedia.org/wiki/Unit_of_work

   Repository
      In :term:`DDD`, a repository is an abstraction to store :term:`domain model`
      objects.