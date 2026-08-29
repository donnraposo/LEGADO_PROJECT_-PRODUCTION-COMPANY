import sys

from PySide6.QtWidgets import QApplication

from legado_agent.adapters.ui.main_window import MainWindow
from legado_agent.application.session import AgentSession
from legado_agent.infrastructure.config import AgentConfig
from legado_agent.infrastructure.persistence.sqlite_analysis_repository import (
    SQLiteAnalysisRepository,
)
from legado_agent.infrastructure.persistence.sqlite_database import SQLiteDatabase
from legado_agent.infrastructure.persistence.sqlite_local_repository import SQLiteLocalRepository
from legado_agent.infrastructure.persistence.sqlite_organization_repository import (
    SQLiteOrganizationRepository,
)
from legado_agent.infrastructure.persistence.sqlite_upload_repository import (
    SQLiteUploadRepository,
)


def ssl_self_test() -> int:
    import ssl

    context = ssl.create_default_context()
    if not context:
        raise RuntimeError("Não foi possível inicializar o suporte SSL.")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return ssl_self_test()
    config = AgentConfig.from_environment()
    database = SQLiteDatabase(config.data_dir / "agent.sqlite3")
    database.migrate()
    repository = SQLiteLocalRepository(database)
    application = QApplication(sys.argv)
    window = MainWindow(
        config,
        repository,
        SQLiteAnalysisRepository(database),
        SQLiteOrganizationRepository(database),
        AgentSession(),
        SQLiteUploadRepository(database),
    )
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
