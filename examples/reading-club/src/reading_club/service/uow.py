from jeepito import AsyncAbstractUnitOfWork
from reading_club.service.repositories import (
    AbstractBookRepository,
    AbstractReviewerRepository,
    AbstractReviewRepository,
    Repositories,
)


class AbstractUnitOfWork(AsyncAbstractUnitOfWork[Repositories]):
    books: AbstractBookRepository
    reviewers: AbstractReviewerRepository
    reviews: AbstractReviewRepository
