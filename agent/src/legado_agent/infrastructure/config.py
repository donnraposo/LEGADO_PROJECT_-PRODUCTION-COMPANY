from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AgentConfig:
    backend_url: str
    oidc_issuer: str
    oidc_client_id: str
    data_dir: Path
    poll_interval_seconds: int = 5
    web_url: str = "http://127.0.0.1:5173"

    @classmethod
    def from_environment(cls) -> AgentConfig:
        default_data = Path(os.environ.get("LOCALAPPDATA", Path.cwd())) / "LEGADO"
        return cls(
            backend_url=os.environ.get("LEGADO_BACKEND_URL", "http://127.0.0.1:8000"),
            oidc_issuer=os.environ.get("LEGADO_OIDC_ISSUER", "http://127.0.0.1:8080/realms/legado"),
            oidc_client_id=os.environ.get("LEGADO_OIDC_CLIENT_ID", "legado-agent"),
            data_dir=Path(os.environ.get("LEGADO_DATA_DIR", default_data)),
            poll_interval_seconds=int(os.environ.get("LEGADO_POLL_INTERVAL", "5")),
            web_url=os.environ.get("LEGADO_WEB_URL", "http://127.0.0.1:5173"),
        )
