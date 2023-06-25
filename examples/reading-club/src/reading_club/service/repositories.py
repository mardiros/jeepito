import abc
import enum
from types import EllipsisType
from typing import Union

from reading_club.domain.model import Book, Review, Reviewer
from result import Result

from messagebus import AsyncAbstractRepository


class BookRepositoryError(enum.Enum):
    integrity_error = "integrity_error"


class ReviewerRepositoryError(enum.Enum):
    integrity_error = "integrity_error"


class ReviewRepositoryError(enum.Enum):
    integrity_error = "integrity_error"


BookRepositoryOperationResult = Result[EllipsisType, BookRepositoryError]
ReviewerRepositoryOperationResult = Result[EllipsisType, ReviewerRepositoryError]
ReviewRepositoryOperationResult = Result[EllipsisType, ReviewRepositoryError]


class AbstractBookRepository(AsyncAbstractRepository):
    @abc.abstractmethod
    async def add(self, model: Book) -> BookRepositoryOperationResult:
        ...


class AbstractReviewerRepository(AsyncAbstractRepository):
    @abc.abstractmethod
    async def add(self, model: Reviewer) -> ReviewerRepositoryOperationResult:
        ...


class AbstractReviewRepository(AsyncAbstractRepository):
    @abc.abstractmethod
    async def add(self, model: Review) -> ReviewRepositoryOperationResult:
        ...


Repositories = Union[
    AbstractBookRepository, AbstractReviewerRepository, AbstractReviewRepository
]
