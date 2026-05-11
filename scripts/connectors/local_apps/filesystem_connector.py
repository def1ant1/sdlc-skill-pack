from __future__ import annotations

from scripts.connectors.base_connector import BaseConnector


class FilesystemConnector(BaseConnector):
    def _authenticate(self) -> None:
        self._auth_headers = {}

    def health_check(self) -> bool:
        return True
