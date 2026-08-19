from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.presentation.http.conflict_error import ConflictError
from modules.companies.adapters.api.company_context import require_company_membership, require_owner
from modules.operations.application.dto.agent_command_summary import AgentCommandSummary
from modules.operations.application.exceptions import (
    CommandIdempotencyConflictError,
    MachineNotFoundError,
)
from modules.operations.application.use_cases.manage_agent_commands_use_case import (
    CreateAgentCommandUseCase,
    ListPendingAgentCommandsUseCase,
)
from modules.operations.infrastructure.persistence.django_operations_repository import (
    DjangoOperationsRepository,
)


class CreateAgentCommandRequestSerializer(serializers.Serializer):
    machine_id = serializers.UUIDField()
    command_type = serializers.CharField(min_length=1, max_length=60)
    resource_type = serializers.CharField(min_length=1, max_length=60)
    resource_id = serializers.UUIDField(required=False, allow_null=True)
    payload = serializers.JSONField(required=False, default=dict)
    idempotency_key = serializers.CharField(min_length=8, max_length=120)

    def validate_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("O payload deve ser um objeto JSON.")
        return value


class AgentCommandCollectionView(APIView):
    def post(self, request) -> Response:
        membership = require_owner(request)
        serializer = CreateAgentCommandRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            command, created = CreateAgentCommandUseCase(
                DjangoOperationsRepository()
            ).execute(
                company_id=membership.company_id,
                user_id=request.user.id,
                **serializer.validated_data,
            )
        except MachineNotFoundError as exc:
            raise NotFound("Máquina não encontrada.") from exc
        except CommandIdempotencyConflictError as exc:
            raise ConflictError("Chave de idempotência reutilizada com outro conteúdo.") from exc
        except ValueError as exc:
            raise ValidationError("O comando contém campo sensível proibido.") from exc
        return Response(
            self._serialize(command),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @staticmethod
    def _serialize(command: AgentCommandSummary) -> dict[str, object]:
        return {
            "id": str(command.id),
            "machine_id": str(command.machine_id),
            "command_type": command.command_type,
            "resource_type": command.resource_type,
            "resource_id": str(command.resource_id) if command.resource_id else None,
            "payload": command.payload,
            "sequence": command.sequence,
            "correlation_id": str(command.correlation_id),
            "status": command.status,
            "progress_percent": command.progress_percent,
            "result": command.result,
            "failure_code": command.failure_code,
            "version": command.version,
        }


class MachineCommandCollectionView(APIView):
    def get(self, request, machine_id) -> Response:
        membership = require_company_membership(request)
        query = serializers.Serializer(data=request.query_params)
        query.fields["after_sequence"] = serializers.IntegerField(
            required=False, min_value=0, default=0
        )
        query.fields["limit"] = serializers.IntegerField(
            required=False, min_value=1, max_value=100, default=50
        )
        query.is_valid(raise_exception=True)
        try:
            commands = ListPendingAgentCommandsUseCase(
                DjangoOperationsRepository()
            ).execute(
                membership.company_id,
                request.user.id,
                machine_id,
                query.validated_data["after_sequence"],
                query.validated_data["limit"],
            )
        except MachineNotFoundError as exc:
            raise NotFound("Máquina não encontrada.") from exc
        return Response(
            {"items": [AgentCommandCollectionView._serialize(item) for item in commands]}
        )
