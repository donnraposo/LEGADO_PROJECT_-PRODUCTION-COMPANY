from uuid import UUID

from modules.audit.infrastructure.persistence.models.audit_event_model import AuditEventModel


class AuditRecorder:
    _EVENT_PRESENTATION = {
        "COMPANY_INVITATION_CREATED": (
            "Convite criado",
            "Um convite de acesso à empresa foi criado.",
        ),
        "COMPANY_INVITATION_ACCEPTED": (
            "Convite aceito",
            "Um convite foi aceito e o vínculo empresarial foi ativado.",
        ),
        "COMPANY_INVITATION_CANCELLED": (
            "Convite cancelado",
            "Um convite pendente foi cancelado.",
        ),
        "COMPANY_MEMBERSHIP_UPDATED": (
            "Membro atualizado",
            "O papel ou estado de um membro da empresa foi alterado.",
        ),
        "PROJECT_ACCESS_GRANTED": (
            "Acesso a projeto concedido",
            "Um Administrador recebeu acesso a um projeto.",
        ),
        "PROJECT_ACCESS_REVOKED": (
            "Acesso a projeto revogado",
            "O acesso de um Administrador a um projeto foi revogado.",
        ),
    }

    @staticmethod
    def record(
        *,
        company_id: UUID,
        actor_user_id: UUID,
        event_type: str,
        subject_type: str,
        subject_id: UUID,
        old_state: dict[str, object] | None = None,
        new_state: dict[str, object] | None = None,
        action_name: str | None = None,
        description: str | None = None,
    ) -> None:
        default_name, default_description = AuditRecorder._EVENT_PRESENTATION.get(
            event_type,
            (event_type.replace("_", " ").title(), "Evento funcional registrado."),
        )
        AuditEventModel.objects.create(
            company_id=company_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            action_name=action_name or default_name,
            description=description or default_description,
            subject_type=subject_type,
            subject_id=subject_id,
            old_state=old_state,
            new_state=new_state,
            change_state=AuditRecorder._changes(old_state, new_state),
        )

    @staticmethod
    def _changes(
        old_state: dict[str, object] | None,
        new_state: dict[str, object] | None,
    ) -> dict[str, dict[str, object | None]]:
        old_values = old_state or {}
        new_values = new_state or {}
        changed: dict[str, dict[str, object | None]] = {}
        for field in sorted(old_values.keys() | new_values.keys()):
            old_value = old_values.get(field)
            new_value = new_values.get(field)
            if old_value != new_value:
                changed[field] = {"old": old_value, "new": new_value}
        return changed
