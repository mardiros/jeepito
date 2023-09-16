from reading_club.service.repositories import AbstractBookRepository

from jeepito import AsyncAbstractUnitOfWork


class AbstractUnitOfWork(AsyncAbstractUnitOfWork[AbstractBookRepository]):
    books: AbstractBookRepository
