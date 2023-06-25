from messagebus import AsyncAbstractUnitOfWork

from reading_club.service.repositories import (
    AbstractBookRepository,
)


class AbstractUnitOfWork(AsyncAbstractUnitOfWork[AbstractBookRepository]):
    books: AbstractBookRepository
