"""
Propagate commands and events to every registered handles.

"""
import logging
from collections import defaultdict
from typing import Any, Dict, List, Type, cast

from messagebus.domain.model import Command, Event, Message
from messagebus.typing import (
    SyncCommandHandler,
    SyncEventHandler,
    SyncMessageHandler,
)

from .unit_of_work import SyncUnitOfWorkTransaction

log = logging.getLogger(__name__)


class ConfigurationError(RuntimeError):
    """Prevents bad usage of the add_listener."""


class SyncMessageRegistry:
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

    def handle(self, message: Message, uow: SyncUnitOfWorkTransaction) -> Any:
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
            idx += 1
        return ret
