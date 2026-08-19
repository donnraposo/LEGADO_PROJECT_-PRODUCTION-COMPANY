from uuid import UUID

from modules.audit.infrastructure.persistence.audit_recorder import AuditRecorder
from modules.catalog.application.ports.catalog_audit import CatalogAudit


class DjangoCatalogAudit(CatalogAudit):
    def record_metadata_updated(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        old_state: dict[str, object],
        new_state: dict[str, object],
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="MEDIA_METADATA_UPDATED",
            action_name="Metadados do arquivo atualizados",
            description="Os metadados funcionais de um arquivo foram alterados.",
            subject_type="media_file",
            subject_id=media_file_id,
            old_state=old_state,
            new_state=new_state,
        )

    def record_state_reconciled(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        machine_id: UUID,
        old_status: str,
        new_status: str,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="MEDIA_FILE_STATE_RECONCILED",
            action_name="Estado técnico do arquivo reconciliado",
            description="O agente local confirmou uma transição técnica do arquivo.",
            subject_type="media_file",
            subject_id=media_file_id,
            old_state={"status": old_status, "machine_id": str(machine_id)},
            new_state={"status": new_status, "machine_id": str(machine_id)},
        )

    def record_tag_changed(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        tag_id: UUID,
        assigned: bool,
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="MEDIA_FILE_TAG_ASSIGNED" if assigned else "MEDIA_FILE_TAG_REMOVED",
            action_name="Tag aplicada ao arquivo" if assigned else "Tag removida do arquivo",
            description=(
                "Uma tag foi aplicada a um arquivo."
                if assigned
                else "Uma tag foi removida de um arquivo."
            ),
            subject_type="media_file",
            subject_id=media_file_id,
            old_state={"tag_id": str(tag_id), "assigned": not assigned},
            new_state={"tag_id": str(tag_id), "assigned": assigned},
        )

    def record_metadata_restored(
        self,
        *,
        company_id: UUID,
        actor_user_id: UUID,
        media_file_id: UUID,
        target_version: int,
        old_state: dict[str, object],
        new_state: dict[str, object],
    ) -> None:
        AuditRecorder.record(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type="MEDIA_METADATA_RESTORED",
            action_name="Metadados do arquivo restaurados",
            description=f"Os metadados foram restaurados a partir da versão {target_version}.",
            subject_type="media_file",
            subject_id=media_file_id,
            old_state=old_state,
            new_state=new_state,
        )
