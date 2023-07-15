import abc
import enum
from types import EllipsisType

from reading_club.domain.model import Book
from result import Result

from messagebus import AsyncAbstractRepository


class BookRepositoryError(enum.Enum):
    integrity_error = "integrity_error"
    not_found = "not_found"


BookRepositoryResult = Result[Book, BookRepositoryError]
BookRepositoryOperationResult = Result[EllipsisType, BookRepositoryError]


class AbstractBookRepository(AsyncAbstractRepository[Book]):
    @abc.abstractmethod
    async def add(self, model: Book) -> BookRepositoryOperationResult:
        ...

    @abc.abstractmethod
    async def get(self, id: str) -> BookRepositoryResult:
        ...
