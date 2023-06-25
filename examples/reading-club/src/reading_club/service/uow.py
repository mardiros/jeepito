from messagebus import AsyncAbstractUnitOfWork

from .repositories import (
    # AbstractReviewRepository, AbstractReviewerRepository, Repositories,
    AbstractBookRepository,
)


class AbstractUnitOfWork(AsyncAbstractUnitOfWork[AbstractBookRepository]):
    books: AbstractBookRepository
    # reviewers: AbstractReviewerRepository
    # reviews: AbstractReviewRepository
