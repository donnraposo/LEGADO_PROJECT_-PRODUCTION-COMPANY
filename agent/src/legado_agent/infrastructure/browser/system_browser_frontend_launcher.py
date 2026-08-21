import webbrowser
from uuid import UUID


class SystemBrowserFrontendLauncher:
    def __init__(self, web_url: str) -> None:
        self._web_url = web_url.rstrip("/")

    def open_catalog(self, company_id: UUID, project_id: UUID) -> bool:
        url = f"{self._web_url}/companies/{company_id}/projects/{project_id}/catalog"
        return webbrowser.open(url, new=2)
