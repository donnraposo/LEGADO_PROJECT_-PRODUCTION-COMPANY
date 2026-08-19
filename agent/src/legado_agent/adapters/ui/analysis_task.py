from threading import Event

from PySide6.QtCore import QRunnable, Slot

from legado_agent.adapters.ui.background_task import TaskSignals
from legado_agent.application.analyze_selection_use_case import AnalyzeSelectionUseCase


class AnalysisTask(QRunnable):
    def __init__(self, use_case: AnalyzeSelectionUseCase, arguments: dict[str, object]) -> None:
        super().__init__()
        self._use_case = use_case
        self._arguments = arguments
        self._cancelled = Event()
        self.signals = TaskSignals()

    def cancel(self) -> None:
        self._cancelled.set()

    @Slot()
    def run(self) -> None:
        try:
            result = self._use_case.execute(
                company_id=self._arguments["company_id"],
                client_name=self._arguments["client_name"],
                project_id=self._arguments["project_id"],
                project_name=self._arguments["project_name"],
                selected_paths=self._arguments["selected_paths"],
                destination_root=self._arguments["destination_root"],
                progress=self.signals.progress.emit,
                cancelled=self._cancelled.is_set,
            )
            self.signals.succeeded.emit(result)
        except Exception as exc:
            self.signals.failed.emit(str(exc))
