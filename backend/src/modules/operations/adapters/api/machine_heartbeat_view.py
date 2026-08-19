from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.companies.adapters.api.company_context import require_company_membership
from modules.operations.application.use_cases.record_machine_heartbeat_use_case import (
    RecordMachineHeartbeatUseCase,
)
from modules.operations.infrastructure.persistence.django_operations_repository import (
    DjangoOperationsRepository,
)


class MachineHeartbeatRequestSerializer(serializers.Serializer):
    installation_id = serializers.UUIDField()
    display_name = serializers.CharField(min_length=1, max_length=120)
    os_family = serializers.ChoiceField(choices=["WINDOWS", "MACOS"])
    agent_version = serializers.CharField(min_length=1, max_length=40)


class MachineHeartbeatView(APIView):
    def post(self, request) -> Response:
        membership = require_company_membership(request)
        serializer = MachineHeartbeatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        machine = RecordMachineHeartbeatUseCase(DjangoOperationsRepository()).execute(
            company_id=membership.company_id,
            user_id=request.user.id,
            **serializer.validated_data,
        )
        return Response(
            {
                "id": str(machine.id),
                "installation_id": str(machine.installation_id),
                "display_name": machine.display_name,
                "os_family": machine.os_family,
                "agent_version": machine.agent_version,
                "status": machine.status,
                "last_seen_at": machine.last_seen_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )
