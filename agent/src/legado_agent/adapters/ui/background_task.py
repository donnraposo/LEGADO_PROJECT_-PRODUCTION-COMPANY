from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class TaskSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int)


class BackgroundTask(QRunnable):
    def __init__(self, operation: Callable[[], object]) -> None:
        super().__init__()
        self._operation = operation
        self.signals = TaskSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.succeeded.emit(self._operation())
        except Exception as exc:
            self.signals.failed.emit(str(exc))
