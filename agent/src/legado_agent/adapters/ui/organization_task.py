from threading import Event

from PySide6.QtCore import QRunnable, Slot

from legado_agent.adapters.ui.background_task import TaskSignals
from legado_agent.application.execute_organization_use_case import (
    ExecuteOrganizationUseCase,
)
from legado_agent.domain.organization_operation import OrganizationOperation


class OrganizationTask(QRunnable):
    def __init__(
        self,
        use_case: ExecuteOrganizationUseCase,
        operation: OrganizationOperation,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._operation = operation
        self._cancelled = Event()
        self.signals = TaskSignals()

    def cancel(self) -> None:
        self._cancelled.set()

    @Slot()
    def run(self) -> None:
        try:
            result = self._use_case.execute(
                self._operation,
                progress=self.signals.progress.emit,
                cancelled=self._cancelled.is_set,
            )
            self.signals.succeeded.emit((self._operation, result))
        except Exception as exc:
            self.signals.failed.emit(str(exc))
