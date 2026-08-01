from types import TracebackType
from typing import Self

from django.db import transaction

from modules.projects.application.ports.unit_of_work import UnitOfWork


class DjangoUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self._atomic = transaction.atomic()

    def __enter__(self) -> Self:
        self._atomic.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return self._atomic.__exit__(exc_type, exc_value, traceback)
