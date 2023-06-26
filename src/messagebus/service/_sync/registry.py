"""
Propagate commands and events to every registered handles.

"""
import importlib
import inspect
import logging
from collections import defaultdict
from typing import Any, Dict, Generic, List, Type, cast

import venusian  # type: ignore

from messagebus.domain.model import Command, Event, Message
from messagebus.typing import (
    SyncCommandHandler,
    SyncEventHandler,
    SyncMessageHandler,
    TCommand,
    TEvent,
    TSyncUow,
)

from .unit_of_work import SyncUnitOfWorkTransaction, TRepositories

log = logging.getLogger(__name__)
VENUSIAN_CATEGORY = "messagebus"


class ConfigurationError(RuntimeError):
    """Prevents bad usage of the add_listener."""


def sync_listen(
    wrapped: SyncMessageHandler[TCommand, TSyncUow, TEvent]
) -> SyncMessageHandler[TCommand, TSyncUow, TEvent]:
    """
    Decorator to listen for a command or an event.

    Note that you can handle one listener for a command, and many for events.
    The command handler result is returned by the handle call of the message bus.
    """

    def callback(
        scanner: venusian.Scanner,
        name: str,
        ob: SyncMessageHandler[TCommand, TSyncUow, TEvent],
    ) -> None:
        if not hasattr(scanner, VENUSIAN_CATEGORY):
            return  # coverage: ignore
        argsspec = inspect.getfullargspec(ob)
        msg_type = argsspec.annotations[argsspec.args[0]]
        scanner.messagebus.add_listener(msg_type, wrapped)  # type: ignore

    venusian.attach(wrapped, callback, category=VENUSIAN_CATEGORY)  # type: ignore
    return wrapped


class SyncMessageBus(Generic[TRepositories]):
    """Store all the handlers for commands an events."""

    def __init__(self) -> None:
        self.commands_registry: Dict[
            Type[Command], SyncCommandHandler[Command, Any]
        ] = {}
        self.events_registry: Dict[
            Type[Event], List[SyncEventHandler[Event, Any]]
        ] = defaultdict(list)

    def add_listener(
        self, msg_type: Type[Message], callback: SyncMessageHandler[Any, Any, Any]
    ) -> None:
        if issubclass(msg_type, Command):
            if msg_type in self.commands_registry:
                raise ConfigurationError(
                    f"{msg_type} command has been registered twice"
                )
            self.commands_registry[msg_type] = cast(
                SyncCommandHandler[Command, Any], callback
            )
        elif issubclass(msg_type, Event):
            self.events_registry[msg_type].append(
                cast(SyncEventHandler[Event, Any], callback)
            )
        else:
            raise ConfigurationError(
                f"Invalid usage of the listen decorator: "
                f"type {msg_type} should be a command or an event"
            )

    def remove_listener(
        self, msg_type: type, callback: SyncMessageHandler[Any, Any, Any]
    ) -> None:
        if issubclass(msg_type, Command):
            if msg_type not in self.commands_registry:
                raise ConfigurationError(f"{msg_type} command has not been registered")
            del self.commands_registry[msg_type]
        elif issubclass(msg_type, Event):
            try:
                self.events_registry[msg_type].remove(
                    cast(SyncEventHandler[Event, Any], callback)
                )
            except ValueError:
                raise ConfigurationError(f"{msg_type} event has not been registered")
        else:
            raise ConfigurationError(
                f"Invalid usage of the listen decorator: "
                f"type {msg_type} should be a command or an event"
            )

    def handle(
        self, message: Message, uow: SyncUnitOfWorkTransaction[TRepositories]
    ) -> Any:
        """
        Notify listener of that event registered with `messagebus.add_listener`.
        Return the first event from the command.
        """
        queue = [message]
        idx = 0
        ret = None
        while queue:
            message = queue.pop(0)
            if not isinstance(message, (Command, Event)):
                raise RuntimeError(f"{message} was not an Event or Command")
            msg_type = type(message)
            if msg_type in self.commands_registry:
                cmdret = self.commands_registry[cast(Type[Command], msg_type)](
                    cast(Command, message), uow
                )
                if idx == 0:
                    ret = cmdret
                queue.extend(uow.uow.collect_new_events())
            elif msg_type in self.events_registry:
                for callback in self.events_registry[cast(Type[Event], msg_type)]:
                    callback(cast(Event, message), uow)
                    queue.extend(uow.uow.collect_new_events())
            uow.eventstore.add(message)
            idx += 1
        return ret

    def scan(
        self,
        *mods: str,
    ) -> None:
        """
        Scan the module (or modules) containing service handlers.

        when a message is handled by the bus, the bus propagate the message
        to hook functions, called :term:`Service Handler` that receive the message,
        and a :term:`Unit Of Work` to process it has a business transaction.
        """
        scanner = venusian.Scanner(messagebus=self)
        for modname in mods:
            if modname.startswith("."):
                raise ValueError(f"{modname}: Relative package unsupported")
            mod = importlib.import_module(modname)
            scanner.scan(mod, categories=[VENUSIAN_CATEGORY])  # type: ignore
