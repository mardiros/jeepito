"""
Propagate commands and events to every registered handles.

"""

import importlib
import inspect
import logging
from collections import defaultdict
from typing import Any, Generic, cast

import venusian  # type: ignore

from messagebus.domain.model import GenericCommand, GenericEvent, Message
from messagebus.typing import AsyncMessageHandler, TAsyncUow, TMessage

from .unit_of_work import AsyncUnitOfWorkTransaction, TRepositories

log = logging.getLogger(__name__)
VENUSIAN_CATEGORY = "messagebus"


class ConfigurationError(RuntimeError):
    """Prevents bad usage of the add_listener."""


def async_listen(
    wrapped: AsyncMessageHandler[TMessage, TAsyncUow],
) -> AsyncMessageHandler[TMessage, TAsyncUow]:
    """
    Decorator to listen for a command or an event.

    Note that you can handle one listener for a command, and many for events.
    The command handler result is returned by the handle call of the message bus.
    """

    def callback(
        scanner: venusian.Scanner,
        name: str,
        ob: AsyncMessageHandler[TMessage, TAsyncUow],
    ) -> None:
        if not hasattr(scanner, VENUSIAN_CATEGORY):
            return  # coverage: ignore
        argsspec = inspect.getfullargspec(ob)
        msg_type = argsspec.annotations[argsspec.args[0]]
        scanner.messagebus.add_listener(msg_type, wrapped)  # type: ignore

    venusian.attach(wrapped, callback, category=VENUSIAN_CATEGORY)  # type: ignore
    return wrapped


class AsyncMessageBus(Generic[TRepositories]):
    """Store all the handlers for commands an events."""

    def __init__(self) -> None:
        self.commands_registry: dict[
            type[GenericCommand[Any]], AsyncMessageHandler[GenericCommand[Any], Any]
        ] = {}
        self.events_registry: dict[
            type[GenericEvent[Any]], list[AsyncMessageHandler[GenericEvent[Any], Any]]
        ] = defaultdict(list)

    def add_listener(
        self, msg_type: type[Message[Any]], callback: AsyncMessageHandler[Any, Any]
    ) -> None:
        if issubclass(msg_type, GenericCommand):
            if msg_type in self.commands_registry:
                raise ConfigurationError(
                    f"{msg_type} command has been registered twice"
                )
            self.commands_registry[msg_type] = callback
        elif issubclass(msg_type, GenericEvent):
            self.events_registry[msg_type].append(callback)
        else:
            raise ConfigurationError(
                f"Invalid usage of the listen decorator: "
                f"type {msg_type} should be a command or an event"
            )

    def remove_listener(
        self, msg_type: type, callback: AsyncMessageHandler[Any, Any]
    ) -> None:
        if issubclass(msg_type, GenericCommand):
            if msg_type not in self.commands_registry:
                raise ConfigurationError(f"{msg_type} command has not been registered")
            del self.commands_registry[msg_type]
        elif issubclass(msg_type, GenericEvent):
            try:
                self.events_registry[msg_type].remove(callback)
            except ValueError as exc:
                raise ConfigurationError(
                    f"{msg_type} event has not been registered"
                ) from exc
        else:
            raise ConfigurationError(
                f"Invalid usage of the listen decorator: "
                f"type {msg_type} should be a command or an event"
            )

    async def handle(
        self, message: Message[Any], uow: AsyncUnitOfWorkTransaction[TRepositories]
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
            if not isinstance(message, (GenericCommand, GenericEvent)):
                raise RuntimeError(f"{message} was not an Event or Command")
            msg_type = type(message)
            if msg_type in self.commands_registry:
                cmdret = await self.commands_registry[msg_type](  # type: ignore
                    cast(GenericCommand[Any], message), uow
                )
                if idx == 0:
                    ret = cmdret
                queue.extend(uow.uow.collect_new_events())
            elif msg_type in self.events_registry:
                for callback in self.events_registry[msg_type]:  # type: ignore
                    await callback(cast(GenericEvent[Any], message), uow)
                    queue.extend(uow.uow.collect_new_events())
            await uow.eventstore.add(message)
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
                raise ValueError(
                    f"scan error: relative package unsupported for {modname}"
                )
            mod = importlib.import_module(modname)
            scanner.scan(mod, categories=[VENUSIAN_CATEGORY])  # type: ignore
