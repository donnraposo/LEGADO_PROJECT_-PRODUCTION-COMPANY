import os
import time
from datetime import UTC, datetime
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QInputDialog

from legado_agent.adapters.ui.main_window import MainWindow
from legado_agent.application.session import AgentSession
from legado_agent.domain.analysis_batch import AnalysisBatch
from legado_agent.domain.analysis_item import AnalysisItem
from legado_agent.infrastructure.config import AgentConfig
from legado_agent.infrastructure.persistence.sqlite_analysis_repository import (
    SQLiteAnalysisRepository,
)
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase
from legado_agent.infrastructure.persistence.sqlite_local_repository import SQLiteLocalRepository
from legado_agent.infrastructure.persistence.sqlite_organization_repository import (
    SQLiteOrganizationRepository,
)


def test_window_starts_disconnected_and_discards_session_on_close(tmp_path) -> None:
    application = QApplication.instance() or QApplication([])
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    session = AgentSession()
    session.start("memory-only")
    window = MainWindow(
        AgentConfig("http://backend", "http://issuer", "agent", tmp_path),
        SQLiteLocalRepository(database),
        SQLiteAnalysisRepository(database),
        SQLiteOrganizationRepository(database),
        session,
    )

    assert window.windowTitle() == "Gerenciador de Áudio Visual — Agente local"
    window.close()
    application.processEvents()

    assert not session.authenticated


def test_preview_checkbox_persists_local_selection(tmp_path) -> None:
    application = QApplication.instance() or QApplication([])
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    repository = SQLiteAnalysisRepository(database)
    company_id = uuid4()
    project_id = uuid4()
    batch = AnalysisBatch(
        uuid4(),
        company_id,
        "Cliente",
        project_id,
        "Projeto",
        (str(tmp_path),),
        str(tmp_path / "organized"),
        "READY",
        datetime.now(UTC),
    )
    item = AnalysisItem(
        uuid4(),
        batch.id,
        str(tmp_path / "clip.mov"),
        "clip.mov",
        "mov",
        "video/quicktime",
        10,
        0,
        None,
        "UNIDENTIFIED",
        "abc",
        "Cliente\\Projeto\\DATA_NAO_IDENTIFICADA\\clip.mov",
        None,
        "",
        "",
        True,
    )
    repository.create_batch(batch)
    repository.save_item(item)
    session = AgentSession()
    session.start("memory-only")
    window = MainWindow(
        AgentConfig("http://backend", "http://issuer", "agent", tmp_path),
        SQLiteLocalRepository(database),
        repository,
        SQLiteOrganizationRepository(database),
        session,
    )

    window._render_analysis(batch, [item])
    window._analysis_table.item(0, 0).setCheckState(Qt.CheckState.Unchecked)
    application.processEvents()

    assert not repository.list_items(batch.id)[0].selected
    window.close()


class FakeCreationBackend:
    def __init__(self) -> None:
        self.companies: list[dict[str, object]] = []
        self.clients: list[dict[str, object]] = []
        self.projects: list[dict[str, object]] = []
        self.machine_id = uuid4()
        self.heartbeats = 0

    def create_company(self, name: str) -> dict[str, object]:
        company = {"id": str(uuid4()), "name": name, "role": "OWNER"}
        self.companies.append(company)
        return company

    def list_clients(self, company_id) -> list[dict[str, object]]:
        return self.clients

    def list_projects(self, company_id) -> list[dict[str, object]]:
        return self.projects

    def create_client(self, company_id, name: str) -> dict[str, object]:
        client = {"id": str(uuid4()), "name": name}
        self.clients.append(client)
        return client

    def create_project(self, company_id, client_id, name: str) -> dict[str, object]:
        project = {"id": str(uuid4()), "client_id": str(client_id), "name": name}
        self.projects.append(project)
        return project

    def heartbeat(self, *args, **kwargs):
        self.heartbeats += 1
        return self.machine_id

    def list_commands(self, company_id, machine_id, after_sequence):
        return []

    def close(self) -> None:
        pass


def test_window_creates_company_client_and_multiple_projects(tmp_path, monkeypatch) -> None:
    application = QApplication.instance() or QApplication([])
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    session = AgentSession()
    window = MainWindow(
        AgentConfig("http://backend", "http://issuer", "agent", tmp_path),
        SQLiteLocalRepository(database),
        SQLiteAnalysisRepository(database),
        SQLiteOrganizationRepository(database),
        session,
    )
    backend = FakeCreationBackend()
    names = iter(["Produtora", "Cliente", "Filme A", "Filme B", "Outro cliente", "Filme C"])
    monkeypatch.setattr(QInputDialog, "getText", lambda *_args: (next(names), True))
    monkeypatch.setattr(
        window, "_run", lambda operation, success, failure=None: success(operation())
    )

    window._login_completed(("memory-only", backend, []))
    assert window._new_company.isEnabled()

    window._new_company.click()
    assert window._company.currentText() == "Produtora — OWNER"
    assert backend.heartbeats == 2
    assert window._connect.isHidden()
    assert window._new_client.isEnabled()

    window._new_client.click()
    assert window._client.currentText() == "Cliente"
    assert window._new_project.isEnabled()

    window._new_project.click()
    window._new_project.click()

    assert [project["name"] for project in backend.projects] == ["Filme A", "Filme B"]
    assert window._project.count() == 2
    assert window._project.currentText() == "Cliente / Filme B"

    window._new_client.click()
    assert window._project.count() == 0
    window._new_project.click()
    assert window._project.currentText() == "Outro cliente / Filme C"

    window._client.setCurrentIndex(0)
    assert window._project.count() == 2
    window.close()
    application.processEvents()


def test_window_only_shows_machine_retry_after_connection_failure(tmp_path) -> None:
    application = QApplication.instance() or QApplication([])
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    window = MainWindow(
        AgentConfig("http://backend", "http://issuer", "agent", tmp_path),
        SQLiteLocalRepository(database),
        SQLiteAnalysisRepository(database),
        SQLiteOrganizationRepository(database),
        AgentSession(),
    )
    window._companies[0] = uuid4()
    window._company.addItem("Produtora — OWNER")

    window._machine_connection_failed("backend indisponível")

    assert window._connect.text() == "Tentar novamente"
    assert not window._connect.isHidden()
    assert window._connect.isEnabled()
    assert window._status.text() == ("Não foi possível conectar esta máquina: backend indisponível")
    window.close()
    application.processEvents()


def test_window_retains_background_task_until_result_is_delivered(tmp_path) -> None:
    application = QApplication.instance() or QApplication([])
    database = SQLiteDatabase(tmp_path / "agent.sqlite3")
    database.migrate()
    window = MainWindow(
        AgentConfig("http://backend", "http://issuer", "agent", tmp_path),
        SQLiteLocalRepository(database),
        SQLiteAnalysisRepository(database),
        SQLiteOrganizationRepository(database),
        AgentSession(),
    )
    results: list[str] = []

    window._run(lambda: "concluída", results.append)

    deadline = time.monotonic() + 2
    while (not results or window._background_tasks) and time.monotonic() < deadline:
        application.processEvents()
        time.sleep(0.01)

    assert results == ["concluída"]
    assert not window._background_tasks
    assert not window._busy
    window.close()
    application.processEvents()
