from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.presentation.http.conflict_error import ConflictError
from modules.companies.adapters.api.company_context import require_company_membership
from modules.operations.adapters.api.agent_command_view import AgentCommandCollectionView
from modules.operations.application.exceptions import (
    AgentCommandNotFoundError,
    AgentCommandVersionConflictError,
    InvalidAgentCommandTransitionError,
)
from modules.operations.application.sensitive_data_policy import SensitiveDataPolicy
from modules.operations.application.use_cases.update_agent_command_state_use_case import (
    UpdateAgentCommandStateUseCase,
)
from modules.operations.infrastructure.persistence.django_operations_repository import (
    DjangoOperationsRepository,
)


class UpdateAgentCommandStateRequestSerializer(serializers.Serializer):
    machine_id = serializers.UUIDField()
    expected_version = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(
        choices=["ACKNOWLEDGED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]
    )
    progress_percent = serializers.IntegerField(min_value=0, max_value=100, default=0)
    result = serializers.JSONField(required=False, default=dict)
    failure_code = serializers.CharField(
        required=False, allow_blank=True, max_length=80, default=""
    )

    def validate_result(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("O resultado deve ser um objeto JSON.")
        if SensitiveDataPolicy.contains_forbidden_key(value):
            raise serializers.ValidationError("O resultado contém campo sensível proibido.")
        return value


class AgentCommandStateView(APIView):
    def patch(self, request, command_id) -> Response:
        membership = require_company_membership(request)
        serializer = UpdateAgentCommandStateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            command = UpdateAgentCommandStateUseCase(
                DjangoOperationsRepository()
            ).execute(
                company_id=membership.company_id,
                user_id=request.user.id,
                machine_id=data["machine_id"],
                command_id=command_id,
                expected_version=data["expected_version"],
                new_status=data["status"],
                progress_percent=data["progress_percent"],
                result=data["result"],
                failure_code=data["failure_code"],
            )
        except AgentCommandNotFoundError as exc:
            raise NotFound("Comando não encontrado para esta máquina.") from exc
        except AgentCommandVersionConflictError as exc:
            raise ConflictError("Versão do comando desatualizada.") from exc
        except InvalidAgentCommandTransitionError as exc:
            raise ValidationError("Transição de estado do comando inválida.") from exc
        return Response(AgentCommandCollectionView._serialize(command))
