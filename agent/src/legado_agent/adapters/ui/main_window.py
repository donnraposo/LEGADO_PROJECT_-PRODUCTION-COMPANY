from pathlib import Path, PureWindowsPath
from uuid import UUID

from PySide6.QtCore import Qt, QThreadPool, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from legado_agent.adapters.ui.analysis_task import AnalysisTask
from legado_agent.adapters.ui.background_task import BackgroundTask
from legado_agent.adapters.ui.organization_task import OrganizationTask
from legado_agent.application.agent_coordinator import AgentCoordinator
from legado_agent.application.analyze_selection_use_case import AnalyzeSelectionUseCase
from legado_agent.application.confirm_organization_use_case import (
    ConfirmOrganizationUseCase,
)
from legado_agent.application.execute_organization_use_case import (
    ExecuteOrganizationUseCase,
)
from legado_agent.application.reconcile_organization_use_case import (
    ReconcileOrganizationUseCase,
)
from legado_agent.application.session import AgentSession
from legado_agent.domain.organization_decision import OrganizationDecision
from legado_agent.infrastructure.config import AgentConfig
from legado_agent.infrastructure.filesystem.safe_file_discovery import SafeFileDiscovery
from legado_agent.infrastructure.filesystem.streaming_sha256 import StreamingSha256
from legado_agent.infrastructure.filesystem.system_metadata_reader import SystemMetadataReader
from legado_agent.infrastructure.filesystem.windows_safe_file_mover import (
    WindowsSafeFileMover,
)
from legado_agent.infrastructure.http.http_backend_gateway import HttpBackendGateway
from legado_agent.infrastructure.identity.oidc_browser_client import OidcBrowserClient
from legado_agent.infrastructure.persistence.sqlite_analysis_repository import (
    SQLiteAnalysisRepository,
)
from legado_agent.infrastructure.persistence.sqlite_local_repository import SQLiteLocalRepository
from legado_agent.infrastructure.persistence.sqlite_organization_repository import (
    SQLiteOrganizationRepository,
)


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AgentConfig,
        repository: SQLiteLocalRepository,
        analysis_repository: SQLiteAnalysisRepository,
        organization_repository: SQLiteOrganizationRepository,
        session: AgentSession,
    ) -> None:
        super().__init__()
        self._config = config
        self._repository = repository
        self._analysis_repository = analysis_repository
        self._organization_repository = organization_repository
        self._session = session
        self._backend: HttpBackendGateway | None = None
        self._coordinator: AgentCoordinator | None = None
        self._analysis_task: AnalysisTask | None = None
        self._organization_task: OrganizationTask | None = None
        self._pool = QThreadPool.globalInstance()
        self._busy = False
        self._companies: dict[int, UUID] = {}
        self._projects: dict[int, tuple[str, UUID, str]] = {}
        self._selected_paths: list[Path] = []
        self._destination_root: Path | None = None
        self._current_batch = None
        self._current_items = []
        self._analysis_item_ids: dict[int, UUID] = {}
        self.setWindowTitle("LEGADO — Agente local")
        self.resize(1180, 720)
        self._build_interface()
        self._timer = QTimer(self)
        self._timer.setInterval(config.poll_interval_seconds * 1000)
        self._timer.timeout.connect(self._poll_once)
        if self._organization_repository.active_operation():
            QTimer.singleShot(0, self._recover_organization)

    def _build_interface(self) -> None:
        self._status = QLabel("Desconectado — autenticação necessária")
        self._login = QPushButton("Entrar")
        self._login.clicked.connect(self._start_login)
        self._company = QComboBox()
        self._company.setEnabled(False)
        self._company.currentIndexChanged.connect(self._company_changed)
        self._connect = QPushButton("Conectar máquina")
        self._connect.setEnabled(False)
        self._connect.clicked.connect(self._connect_machine)
        self._poll = QPushButton("Atualizar fila")
        self._poll.setEnabled(False)
        self._poll.clicked.connect(self._poll_once)
        session_controls = QHBoxLayout()
        session_controls.addWidget(self._login)
        session_controls.addWidget(self._company)
        session_controls.addWidget(self._connect)
        session_controls.addWidget(self._poll)

        self._project = QComboBox()
        self._project.setEnabled(False)
        self._project.currentIndexChanged.connect(self._project_changed)
        self._choose_folder = QPushButton("Selecionar pasta")
        self._choose_folder.setEnabled(False)
        self._choose_folder.clicked.connect(self._select_folder)
        self._choose_files = QPushButton("Selecionar arquivos")
        self._choose_files.setEnabled(False)
        self._choose_files.clicked.connect(self._select_files)
        self._choose_destination = QPushButton("Selecionar destino")
        self._choose_destination.setEnabled(False)
        self._choose_destination.clicked.connect(self._select_destination)
        self._analyze = QPushButton("Analisar e gerar prévia")
        self._analyze.setEnabled(False)
        self._analyze.clicked.connect(self._start_analysis)
        self._cancel_analysis = QPushButton("Cancelar análise")
        self._cancel_analysis.setEnabled(False)
        self._cancel_analysis.clicked.connect(self._cancel_current_analysis)
        self._organize = QPushButton("Confirmar e organizar")
        self._organize.setEnabled(False)
        self._organize.clicked.connect(self._confirm_organization)
        self._cancel_organization = QPushButton("Interromper organização")
        self._cancel_organization.setEnabled(False)
        self._cancel_organization.clicked.connect(self._cancel_current_organization)
        analysis_controls = QHBoxLayout()
        analysis_controls.addWidget(QLabel("Cliente / projeto:"))
        analysis_controls.addWidget(self._project)
        analysis_controls.addWidget(self._choose_folder)
        analysis_controls.addWidget(self._choose_files)
        analysis_controls.addWidget(self._choose_destination)
        analysis_controls.addWidget(self._analyze)
        analysis_controls.addWidget(self._cancel_analysis)
        analysis_controls.addWidget(self._organize)
        analysis_controls.addWidget(self._cancel_organization)

        self._selection_label = QLabel("Nenhum arquivo ou pasta selecionado")
        self._destination_label = QLabel("Destino-base não selecionado")
        self._analysis_progress = QProgressBar()
        self._analysis_progress.setRange(0, 1)
        self._analysis_progress.setValue(0)
        self._analysis_table = QTableWidget(0, 10)
        self._analysis_table.setHorizontalHeaderLabels(
            [
                "Usar",
                "Origem",
                "Destino previsto",
                "Data",
                "Origem da data",
                "Tipo",
                "Bytes",
                "SHA-256",
                "Avisos",
                "Organização",
            ]
        )
        self._analysis_table.itemChanged.connect(self._analysis_selection_changed)

        self._command_table = QTableWidget(0, 4)
        self._command_table.setHorizontalHeaderLabels(
            ["Sequência", "Comando", "Estado", "Progresso"]
        )
        layout = QVBoxLayout()
        layout.addWidget(self._status)
        layout.addLayout(session_controls)
        layout.addLayout(analysis_controls)
        layout.addWidget(self._selection_label)
        layout.addWidget(self._destination_label)
        layout.addWidget(self._analysis_progress)
        layout.addWidget(
            QLabel("Prévia local — movimentação somente após confirmação explícita")
        )
        layout.addWidget(self._analysis_table, 3)
        layout.addWidget(QLabel("Fila de comandos"))
        layout.addWidget(self._command_table, 1)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _start_login(self) -> None:
        self._login.setEnabled(False)
        self._status.setText("Aguardando autenticação no navegador...")

        def login():
            token = OidcBrowserClient(
                self._config.oidc_issuer, self._config.oidc_client_id
            ).login()
            backend = HttpBackendGateway(self._config.backend_url, token)
            try:
                companies = backend.list_companies()
            except Exception:
                backend.close()
                raise
            return token, backend, companies

        self._run(login, self._login_completed)

    def _login_completed(self, result: object) -> None:
        token, backend, companies = result
        self._session.start(token)
        self._backend = backend
        self._company.blockSignals(True)
        self._company.clear()
        self._companies.clear()
        for index, company in enumerate(companies):
            self._company.addItem(f"{company['name']} — {company['role']}")
            self._companies[index] = UUID(str(company["id"]))
        self._company.blockSignals(False)
        self._company.setEnabled(bool(companies))
        self._login.setEnabled(False)
        if companies:
            self._company_changed(self._company.currentIndex())
        else:
            self._status.setText("Autenticado — nenhuma empresa disponível")

    def _company_changed(self, _index: int) -> None:
        company_id = self._company_id()
        self._timer.stop()
        self._coordinator = None
        self._poll.setEnabled(False)
        self._connect.setEnabled(company_id is not None)
        self._clear_projects()
        if self._backend is None or company_id is None:
            return
        self._status.setText("Carregando clientes e projetos...")

        def load_context():
            clients = self._backend.list_clients(company_id)
            projects = self._backend.list_projects(company_id)
            client_names = {str(item["id"]): str(item["name"]) for item in clients}
            return company_id, [
                (
                    client_names.get(
                        str(project["client_id"]), "Cliente desconhecido"
                    ),
                    UUID(str(project["id"])),
                    str(project["name"]),
                )
                for project in projects
            ]

        self._run(load_context, self._projects_completed)

    def _projects_completed(self, projects: object) -> None:
        loaded_company_id, projects = projects
        if loaded_company_id != self._company_id():
            return
        self._project.blockSignals(True)
        for index, context in enumerate(projects):
            client_name, _project_id, project_name = context
            self._project.addItem(f"{client_name} / {project_name}")
            self._projects[index] = context
        self._project.blockSignals(False)
        self._project.setEnabled(bool(self._projects))
        self._update_analysis_controls()
        if self._projects:
            self._project_changed(self._project.currentIndex())
            self._status.setText("Autenticado — selecione arquivos para analisar")
        else:
            self._status.setText("Autenticado — nenhum projeto acessível")

    def _clear_projects(self) -> None:
        self._project.blockSignals(True)
        self._project.clear()
        self._project.blockSignals(False)
        self._projects.clear()
        self._project.setEnabled(False)
        self._selected_paths.clear()
        self._destination_root = None
        self._current_batch = None
        self._current_items = []
        self._selection_label.setText("Nenhum arquivo ou pasta selecionado")
        self._destination_label.setText("Destino-base não selecionado")
        self._update_analysis_controls()

    def _connect_machine(self) -> None:
        company_id = self._company_id()
        if self._backend is None or company_id is None:
            return
        self._coordinator = AgentCoordinator(self._repository, self._backend)
        self._status.setText("Registrando presença da máquina...")
        self._run(lambda: self._coordinator.connect(company_id), self._machine_connected)

    def _machine_connected(self, machine_id: object) -> None:
        self._status.setText(f"Máquina online: {machine_id}")
        self._poll.setEnabled(True)
        self._timer.start()
        self._poll_once()

    def _poll_once(self) -> None:
        company_id = self._company_id()
        if self._coordinator is None or company_id is None or self._busy:
            return
        self._run(lambda: self._coordinator.poll_once(company_id), self._poll_completed)

    def _poll_completed(self, processed: object) -> None:
        self._refresh_command_table()
        self._status.setText(f"Máquina online — {processed} comando(s) processado(s)")

    def _refresh_command_table(self) -> None:
        company_id = self._company_id()
        if company_id is None:
            return
        commands = self._repository.list_commands(company_id)
        self._command_table.setRowCount(len(commands))
        for row, command in enumerate(commands):
            values = (
                str(command.sequence),
                command.command_type,
                command.status,
                f"{command.progress_percent}%",
            )
            for column, value in enumerate(values):
                self._command_table.setItem(row, column, QTableWidgetItem(value))

    def _select_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Selecionar pasta para análise")
        if selected:
            self._add_selected_paths([Path(selected)])

    def _select_files(self) -> None:
        selected, _filter = QFileDialog.getOpenFileNames(
            self, "Selecionar arquivos para análise"
        )
        self._add_selected_paths([Path(path) for path in selected])

    def _select_destination(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self, "Selecionar pasta-base da organização"
        )
        if selected:
            self._destination_root = Path(selected)
            self._destination_label.setText(f"Destino-base: {selected}")
            self._update_analysis_controls()

    def _add_selected_paths(self, paths: list[Path]) -> None:
        existing = {str(path).casefold() for path in self._selected_paths}
        for path in paths:
            if str(path).casefold() not in existing:
                self._selected_paths.append(path)
                existing.add(str(path).casefold())
        count = len(self._selected_paths)
        self._selection_label.setText(f"{count} origem(ns) selecionada(s)")
        self._update_analysis_controls()

    def _start_analysis(self) -> None:
        company_id = self._company_id()
        context = self._project_context()
        if (
            company_id is None
            or context is None
            or not self._selected_paths
            or self._destination_root is None
        ):
            return
        client_name, project_id, project_name = context
        use_case = AnalyzeSelectionUseCase(
            self._analysis_repository,
            SafeFileDiscovery(),
            SystemMetadataReader(),
            StreamingSha256(),
        )
        self._analysis_task = AnalysisTask(
            use_case,
            {
                "company_id": company_id,
                "client_name": client_name,
                "project_id": project_id,
                "project_name": project_name,
                "selected_paths": list(self._selected_paths),
                "destination_root": self._destination_root,
            },
        )
        self._analysis_task.signals.progress.connect(self._analysis_progressed)
        self._analysis_task.signals.succeeded.connect(self._analysis_completed)
        self._analysis_task.signals.failed.connect(self._analysis_failed)
        self._analysis_progress.setRange(0, 0)
        self._cancel_analysis.setEnabled(True)
        self._status.setText("Analisando arquivos sem modificar a origem...")
        self._update_analysis_controls()
        self._pool.start(self._analysis_task)

    def _analysis_progressed(self, current: int, total: int) -> None:
        self._analysis_progress.setRange(0, max(total, 1))
        self._analysis_progress.setValue(current)
        self._status.setText(f"Analisando arquivo {current} de {total}...")

    def _analysis_completed(self, result: object) -> None:
        batch, items = result
        self._analysis_task = None
        self._cancel_analysis.setEnabled(False)
        self._render_analysis(batch, items)
        self._update_analysis_controls()
        self._status.setText(
            f"Prévia {batch.status.lower()} — {len(items)} arquivo(s) analisado(s)"
        )

    def _analysis_failed(self, message: str) -> None:
        self._analysis_task = None
        self._cancel_analysis.setEnabled(False)
        self._analysis_progress.setRange(0, 1)
        self._analysis_progress.setValue(0)
        self._update_analysis_controls()
        self._status.setText(f"Falha na análise: {message}")

    def _cancel_current_analysis(self) -> None:
        if self._analysis_task:
            self._analysis_task.cancel()
            self._status.setText("Cancelamento solicitado; finalizando o arquivo atual...")

    def _project_changed(self, _index: int) -> None:
        self._update_analysis_controls()
        company_id = self._company_id()
        context = self._project_context()
        if company_id is None or context is None:
            return
        _client_name, project_id, _project_name = context
        batch = self._analysis_repository.latest_batch(company_id, project_id)
        if batch:
            self._destination_root = (
                Path(batch.destination_root) if batch.destination_root else None
            )
            self._destination_label.setText(
                f"Destino-base: {batch.destination_root}"
                if batch.destination_root
                else "Prévia antiga sem destino-base; execute nova análise"
            )
            self._render_analysis(batch, self._analysis_repository.list_items(batch.id))
            self._status.setText(f"Prévia anterior recuperada — estado {batch.status}")

    def _render_analysis(self, batch, items) -> None:
        self._current_batch = batch
        self._current_items = items
        self._analysis_table.blockSignals(True)
        self._analysis_item_ids.clear()
        self._analysis_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self._analysis_item_ids[row] = item.id
            selection = QTableWidgetItem()
            selection.setFlags(selection.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            selection.setCheckState(
                Qt.CheckState.Checked if item.selected else Qt.CheckState.Unchecked
            )
            self._analysis_table.setItem(row, 0, selection)
            values = (
                item.source_path,
                item.destination_path,
                item.file_date.isoformat() if item.file_date else "Não identificada",
                item.date_source,
                item.media_type,
                str(item.size_bytes),
                item.checksum_sha256,
                item.warning,
            )
            for column, value in enumerate(values, start=1):
                self._analysis_table.setItem(row, column, QTableWidgetItem(value))
            self._analysis_table.setItem(row, 9, QTableWidgetItem("Pendente"))
        self._analysis_table.blockSignals(False)
        self._analysis_progress.setRange(0, max(len(items), 1))
        self._analysis_progress.setValue(len(items))

    def _analysis_selection_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != 0:
            return
        item_id = self._analysis_item_ids.get(item.row())
        if item_id:
            self._analysis_repository.set_item_selected(
                item_id, item.checkState() == Qt.CheckState.Checked
            )
            if self._current_batch:
                self._current_items = self._analysis_repository.list_items(
                    self._current_batch.id
                )
            self._update_analysis_controls()

    def _confirm_organization(self) -> None:
        active = self._organization_repository.active_operation()
        if active is not None:
            if active.company_id != self._company_id():
                QMessageBox.warning(
                    self,
                    "Empresa diferente",
                    "A organização interrompida pertence a outra empresa.",
                )
                return
            self._start_organization_task(active)
            return
        if self._current_batch is None:
            return
        self._current_items = self._analysis_repository.list_items(
            self._current_batch.id
        )
        decisions = self._collect_organization_decisions()
        if decisions is None:
            return
        selected = [item for item in self._current_items if item.selected]
        total_bytes = sum(item.size_bytes for item in selected)
        confirmed = QMessageBox.question(
            self,
            "Confirmar organização",
            f"Mover {len(selected)} arquivo(s), totalizando {total_bytes} bytes?\n\n"
            "Nenhum destino existente será sobrescrito.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        try:
            operation = ConfirmOrganizationUseCase(
                self._organization_repository, WindowsSafeFileMover()
            ).execute(self._current_batch, self._current_items, decisions)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Organização não confirmada", str(exc))
            return
        self._start_organization_task(operation)

    def _collect_organization_decisions(self) -> list[OrganizationDecision] | None:
        decisions: list[OrganizationDecision] = []
        for item in self._current_items:
            if not item.selected:
                continue
            destination_exists = self._planned_destination(item.destination_path).exists()
            if destination_exists or item.conflict_type == "NAME_CONFLICT":
                decision = self._name_conflict_decision(item)
            elif item.conflict_type == "DUPLICATE_CONTENT":
                decision = self._duplicate_decision(item)
            elif item.conflict_type:
                QMessageBox.warning(self, "Item inválido", item.warning)
                return None
            else:
                continue
            if decision is None:
                return None
            decisions.append(decision)
        return decisions

    def _name_conflict_decision(self, item) -> OrganizationDecision | None:
        options = [
            "Renomear automaticamente",
            "Informar outro nome",
            "Ignorar arquivo",
            "Cancelar organização",
        ]
        choice, accepted = QInputDialog.getItem(
            self,
            "Conflito de destino",
            f"Decisão para {item.name}:",
            options,
            0,
            False,
        )
        if not accepted or choice == options[3]:
            return None
        if choice == options[0]:
            return OrganizationDecision(item.id, "AUTO_RENAME")
        if choice == options[2]:
            return OrganizationDecision(item.id, "SKIP")
        resolved_name, accepted = QInputDialog.getText(
            self, "Novo nome", f"Novo nome completo para {item.name}:"
        )
        if not accepted:
            return None
        return OrganizationDecision(item.id, "RENAME", resolved_name)

    def _duplicate_decision(self, item) -> OrganizationDecision | None:
        options = ["Manter ambos", "Ignorar arquivo", "Cancelar organização"]
        choice, accepted = QInputDialog.getItem(
            self,
            "Conteúdo duplicado",
            f"Decisão para {item.name}:",
            options,
            0,
            False,
        )
        if not accepted or choice == options[2]:
            return None
        return OrganizationDecision(
            item.id, "KEEP" if choice == options[0] else "SKIP"
        )

    def _planned_destination(self, relative_path: str) -> Path:
        if self._destination_root is None:
            return Path(relative_path)
        return self._destination_root.joinpath(*PureWindowsPath(relative_path).parts)

    def _start_organization_task(self, operation) -> None:
        machine_id = self._repository.machine_id(operation.company_id)
        if self._backend is None or machine_id is None:
            QMessageBox.warning(
                self,
                "Máquina não conectada",
                "Conecte esta máquina antes de organizar os arquivos.",
            )
            return
        self._organization_task = OrganizationTask(
            ExecuteOrganizationUseCase(
                self._organization_repository,
                WindowsSafeFileMover(),
                self._backend,
                machine_id,
            ),
            operation,
        )
        self._organization_task.signals.progress.connect(self._organization_progressed)
        self._organization_task.signals.succeeded.connect(self._organization_completed)
        self._organization_task.signals.failed.connect(self._organization_failed)
        self._cancel_organization.setEnabled(True)
        self._status.setText("Organizando arquivos com checkpoints...")
        self._update_analysis_controls()
        self._pool.start(self._organization_task)

    def _organization_progressed(self, current: int, total: int) -> None:
        self._analysis_progress.setRange(0, max(total, 1))
        self._analysis_progress.setValue(current)
        self._status.setText(f"Organizando arquivo {current} de {total}...")

    def _organization_completed(self, result: object) -> None:
        operation, status = result
        self._organization_task = None
        self._cancel_organization.setEnabled(False)
        self._render_organization_status(operation.id)
        self._status.setText(f"Organização finalizada — estado {status}")
        self._update_analysis_controls()

    def _organization_failed(self, message: str) -> None:
        self._organization_task = None
        self._cancel_organization.setEnabled(False)
        self._status.setText(f"Falha na organização: {message}")
        self._update_analysis_controls()

    def _cancel_current_organization(self) -> None:
        if self._organization_task:
            self._organization_task.cancel()
            self._status.setText("Interrupção solicitada; finalizando o arquivo atual...")

    def _render_organization_status(self, operation_id: UUID) -> None:
        rows_by_item = {item_id: row for row, item_id in self._analysis_item_ids.items()}
        for item in self._organization_repository.list_items(operation_id):
            row = rows_by_item.get(item.analysis_item_id)
            if row is not None:
                value = item.status
                if item.error_message:
                    value = f"{value}: {item.error_message}"
                self._analysis_table.setItem(row, 9, QTableWidgetItem(value))

    def _recover_organization(self) -> None:
        self._run(
            lambda: ReconcileOrganizationUseCase(
                self._organization_repository, WindowsSafeFileMover()
            ).execute(),
            self._organization_recovered,
        )

    def _organization_recovered(self, operation: object) -> None:
        if operation is not None:
            self._status.setText(
                "Organização interrompida recuperada; autentique-se para retomar."
            )
            self._render_organization_status(operation.id)
        self._update_analysis_controls()

    def _update_analysis_controls(self) -> None:
        available = (
            self._session.authenticated
            and self._project_context() is not None
            and self._analysis_task is None
            and self._organization_task is None
        )
        self._choose_folder.setEnabled(available)
        self._choose_files.setEnabled(available)
        self._choose_destination.setEnabled(available)
        self._analyze.setEnabled(
            available
            and bool(self._selected_paths)
            and self._destination_root is not None
        )
        active = self._organization_repository.active_operation()
        resumable = active is not None and active.company_id == self._company_id()
        ready = (
            self._current_batch is not None
            and self._current_batch.status == "READY"
            and any(item.selected for item in self._current_items)
        )
        self._organize.setText(
            "Retomar organização" if resumable else "Confirmar e organizar"
        )
        self._organize.setEnabled(available and (resumable or ready))

    def _run(self, operation, success) -> None:
        self._busy = True
        task = BackgroundTask(operation)
        task.signals.succeeded.connect(lambda result: self._task_succeeded(success, result))
        task.signals.failed.connect(self._task_failed)
        self._pool.start(task)

    def _task_succeeded(self, callback, result: object) -> None:
        self._busy = False
        callback(result)

    def _task_failed(self, message: str) -> None:
        self._busy = False
        self._login.setEnabled(not self._session.authenticated)
        self._status.setText(f"Falha operacional: {message}")

    def _company_id(self) -> UUID | None:
        return self._companies.get(self._company.currentIndex())

    def _project_context(self) -> tuple[str, UUID, str] | None:
        return self._projects.get(self._project.currentIndex())

    def closeEvent(self, event) -> None:  # noqa: N802 - nome definido pela API Qt
        self._timer.stop()
        if self._analysis_task:
            self._analysis_task.cancel()
        if self._organization_task:
            self._organization_task.cancel()
        self._session.clear()
        if self._backend:
            self._backend.close()
        super().closeEvent(event)
