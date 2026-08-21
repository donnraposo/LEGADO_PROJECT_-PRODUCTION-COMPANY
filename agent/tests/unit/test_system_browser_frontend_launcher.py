from unittest.mock import patch
from uuid import uuid4

from legado_agent.infrastructure.browser.system_browser_frontend_launcher import (
    SystemBrowserFrontendLauncher,
)


def test_launcher_opens_exact_company_project_catalog() -> None:
    company_id = uuid4()
    project_id = uuid4()

    with patch("webbrowser.open", return_value=True) as opened:
        result = SystemBrowserFrontendLauncher("http://web.local/").open_catalog(
            company_id, project_id
        )

    assert result is True
    opened.assert_called_once_with(
        f"http://web.local/companies/{company_id}/projects/{project_id}/catalog",
        new=2,
    )
