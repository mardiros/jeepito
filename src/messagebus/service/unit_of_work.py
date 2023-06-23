import enum
from typing import TypeVar


class TransactionError(RuntimeError):
    ...


class TransactionStatus(enum.Enum):
    running = "running"
    rolledback = "rolledback"
    committed = "committed"
    closed = "closed"


TRepositories = TypeVar("TRepositories")
