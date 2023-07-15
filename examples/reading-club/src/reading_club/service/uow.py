from reading_club.service.repositories import (
    AbstractBookRepository,
    AbstractReviewerRepository,
    AbstractReviewRepository,
    Repositories,
)

from messagebus import AsyncAbstractUnitOfWork


class AbstractUnitOfWork(AsyncAbstractUnitOfWork[Repositories]):
    books: AbstractBookRepository
    reviewers: AbstractReviewerRepository
    reviews: AbstractReviewRepository
