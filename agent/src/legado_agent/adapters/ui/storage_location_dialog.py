from pathlib import Path

from PySide6.QtCore import QStorageInfo
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StorageLocationDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        title: str,
        message: str,
        allow_folder: bool,
        initial_path: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self._selected_path: Path | None = None
        self._initial_path = initial_path
        self.setWindowTitle(title)
        self.setMinimumWidth(560)

        self._media = QComboBox()
        for label, path in self.available_media():
            self._media.addItem(label, path)
        if initial_path is not None:
            initial_root = Path(initial_path.anchor)
            for index in range(self._media.count()):
                if Path(self._media.itemData(index)) == initial_root:
                    self._media.setCurrentIndex(index)
                    break

        use_media = QPushButton("Usar mídia selecionada")
        use_media.setEnabled(self._media.count() > 0)
        use_media.clicked.connect(self._accept_media)
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)

        actions = QHBoxLayout()
        actions.addWidget(use_media)
        if allow_folder:
            choose_folder = QPushButton("Escolher pasta no PC")
            choose_folder.clicked.connect(self._choose_folder)
            actions.addWidget(choose_folder)
        actions.addWidget(cancel)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        layout.addWidget(QLabel("Mídias disponíveis:"))
        layout.addWidget(self._media)
        layout.addLayout(actions)
        self.setLayout(layout)

    @staticmethod
    def available_media() -> list[tuple[str, Path]]:
        media: list[tuple[str, Path]] = []
        seen: set[str] = set()
        for storage in QStorageInfo.mountedVolumes():
            if not storage.isValid() or not storage.isReady():
                continue
            root = Path(storage.rootPath())
            key = str(root).casefold()
            if key in seen:
                continue
            seen.add(key)
            name = storage.displayName().strip() or "Disco local"
            capacity = StorageLocationDialog._format_size(storage.bytesTotal())
            media.append((f"{name} ({root}) — {capacity}", root))
        return sorted(media, key=lambda item: str(item[1]).casefold())

    @staticmethod
    def _format_size(size: int) -> str:
        value = float(max(size, 0))
        units = ("B", "KB", "MB", "GB", "TB")
        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
            value /= 1024
        return "0 B"

    def _accept_media(self) -> None:
        selected = self._media.currentData()
        if selected:
            self._selected_path = Path(selected)
            self.accept()

    def _choose_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Escolher pasta no PC",
            str(self._initial_path or ""),
        )
        if selected:
            self._selected_path = Path(selected)
            self.accept()

    @classmethod
    def choose_media(cls, parent: QWidget | None) -> Path | None:
        dialog = cls(
            parent,
            "Selecionar HARD DISK",
            "Escolha o HARD DISK que contém os arquivos a analisar.",
            False,
        )
        return dialog._selected_path if dialog.exec() == QDialog.DialogCode.Accepted else None

    @classmethod
    def choose_destination(
        cls, parent: QWidget | None, initial_path: Path | None
    ) -> Path | None:
        dialog = cls(
            parent,
            "Destino da organização",
            "Escolha a mídia ou uma pasta no PC onde o projeto será organizado.",
            True,
            initial_path,
        )
        return dialog._selected_path if dialog.exec() == QDialog.DialogCode.Accepted else None
