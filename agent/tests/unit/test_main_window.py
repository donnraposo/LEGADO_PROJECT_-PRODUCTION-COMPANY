import os
from datetime import UTC, datetime
from uuid import uuid4

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

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

    assert window.windowTitle() == "LEGADO — Agente local"
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
