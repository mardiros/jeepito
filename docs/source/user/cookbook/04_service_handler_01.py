from reading_club.domain.messages import RegisterBook
from reading_club.service.repositories import BookRepositoryOperationResult

from messagebus import AsyncUnitOfWorkTransaction


async def register_book(
    cmd: RegisterBook, uow: AsyncUnitOfWorkTransaction
) -> BookRepositoryOperationResult:
    raise NotImplementedError
