from types import ModuleType
from typing import TYPE_CHECKING, Any, Union

import venusian  # type: ignore

if TYPE_CHECKING:
    from messagebus.service._async.registry import (  # coverage: ignore
        AsyncMessageRegistry,
    )
    from messagebus.service._sync.registry import (  # coverage: ignore
        SyncMessageRegistry,
    )

VENUSIAN_CATEGORY = "messagebus"


def scan(
    bus: Union["AsyncMessageRegistry[Any]", "SyncMessageRegistry[Any]"],
    *mods: ModuleType,
) -> None:
    """
    Scan the module (or modules) containing service handlers.

    when a message is handled by the bus, the bus propagate the message
    to hook functions, called :term:`Service Handler` that receive the message,
    and a :term:`Unit Of Work` to process it has a business transaction.
    """
    scanner = venusian.Scanner(messagebus=bus)
    for mod in mods:
        scanner.scan(mod, categories=[VENUSIAN_CATEGORY])  # type: ignore
