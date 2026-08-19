from django.urls import path

from modules.operations.adapters.api.agent_command_state_view import AgentCommandStateView
from modules.operations.adapters.api.agent_command_view import (
    AgentCommandCollectionView,
    MachineCommandCollectionView,
)
from modules.operations.adapters.api.machine_heartbeat_view import MachineHeartbeatView

urlpatterns = [
    path(
        "agent/machines/heartbeat",
        MachineHeartbeatView.as_view(),
        name="machine-heartbeat",
    ),
    path("agent/commands", AgentCommandCollectionView.as_view(), name="agent-command-create"),
    path(
        "agent/commands/<uuid:command_id>",
        AgentCommandStateView.as_view(),
        name="agent-command-state",
    ),
    path(
        "agent/machines/<uuid:machine_id>/commands",
        MachineCommandCollectionView.as_view(),
        name="machine-command-list",
    ),
]
