# backend/app/openproject_api/client.py
"""
Cliente simples para a API do OpenProject (API v3).

Autenticacao:
- Via API key usando Basic Auth:
    username="apikey"
    password="<SUA_CHAVE>"
  (padrao do OpenProject)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests


class OpenProjectAPIError(RuntimeError):
    """Erro levantado quando a API retorna status >= 400."""


@dataclass(frozen=True)
class OpenProjectClient:
    """Cliente HTTP minimalista para a API v3 do OpenProject."""

    base_url: str
    api_key: str
    timeout: int = 30
    verify: bool = True

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("base_url vazio (configure OPENPROJECT_BASE_URL)")
        if not self.api_key:
            raise ValueError("api_key vazia (configure OPENPROJECT_API_KEY)")

    @property
    def api_root(self) -> str:
        """URL base para a API v3, sempre com barra final."""
        root = self.base_url.rstrip("/") + "/"
        return urljoin(root, "api/v3/")

    def _session(self) -> requests.Session:
        """Cria uma sessao com headers e autenticacao configurados."""
        session = requests.Session()
        session.auth = ("apikey", self.api_key)
        session.headers.update(
            {
                "Accept": "application/hal+json, application/json",
                "User-Agent": "openproject-collector/1.0",
            }
        )
        # Controla validacao SSL (utile para servidores internos com cert autoassinado)
        session.verify = self.verify
        return session

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET basico com tratamento de erro."""
        url = urljoin(self.api_root, path.lstrip("/"))
        with self._session() as session:
            response = session.get(url, params=params, timeout=self.timeout)
            if response.status_code >= 400:
                raise OpenProjectAPIError(
                    f"GET {url} -> {response.status_code}: {response.text[:500]}"
                )
            return response.json()

    def list_projects(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Retorna projetos como list[dict] no schema do Power BI:
        project_id, project_name, project_status, project_href, updated_at
        """
        out: List[Dict[str, Any]] = []
        offset = 1
        total = None

        # API v3 usa offset baseado em pagina (1..n)
        while total is None or (offset - 1) < total:
            data = self._get("projects", params={"pageSize": page_size, "offset": offset})
            total = int(data.get("total", 0))
            count = int(data.get("count", 0))

            embedded = data.get("_embedded", {}) or {}
            elements = embedded.get("elements", []) or []

            for project in elements:
                links = project.get("_links", {}) or {}
                out.append(
                    {
                        "project_id": project.get("id"),
                        "project_name": project.get("name"),
                        "project_status": (project.get("status") or ""),
                        "project_href": (links.get("self", {}) or {}).get("href"),
                        "updated_at": project.get("updatedAt") or project.get("updated_at"),
                    }
                )

            if count <= 0:
                break
            offset += 1

        return out

    def list_work_packages(
        self,
        page_size: int = 200,
        filters_json: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Coleta work packages e retorna no schema do Power BI.

        filters_json:
          string JSON no formato aceito pela API v3 (query param "filters")
          Exemplo:
            '[{"status":{"operator":"o","values":[]}}]'
        """
        out: List[Dict[str, Any]] = []
        offset = 1
        total = None

        params: Dict[str, Any] = {"pageSize": page_size, "offset": offset}
        if filters_json is not None and filters_json != "":
            params["filters"] = filters_json
        else:
            # API v3 aplica filtro padrao (status aberto) quando "filters" nao e enviado.
            # Enviar [] garante retorno de todos os itens.
            params["filters"] = "[]"

        while total is None or (offset - 1) < total:
            params["offset"] = offset
            data = self._get("work_packages", params=params)
            total = int(data.get("total", 0))
            count = int(data.get("count", 0))

            embedded = data.get("_embedded", {}) or {}
            elements = embedded.get("elements", []) or []

            for wp in elements:
                links = wp.get("_links", {}) or {}

                def link_title(key: str) -> str:
                    return (links.get(key, {}) or {}).get("title") or ""

                project = links.get("project", {}) or {}
                out.append(
                    {
                        "wp_id": wp.get("id"),
                        "wp_subject": wp.get("subject"),
                        "wp_type": link_title("type"),
                        "wp_status": link_title("status"),
                        "wp_priority": link_title("priority"),
                        "project_id": _id_from_href(project.get("href") or ""),
                        "project_name": project.get("title") or "",
                        "assignee": link_title("assignee"),
                        "author": link_title("author"),
                        "start_date": wp.get("startDate") or wp.get("start_date"),
                        "due_date": wp.get("dueDate") or wp.get("due_date"),
                        "done_ratio": wp.get("percentageDone") or wp.get("done_ratio"),
                        "created_at": wp.get("createdAt") or wp.get("created_at"),
                        "updated_at": wp.get("updatedAt") or wp.get("updated_at"),
                    }
                )

            if count <= 0:
                break
            offset += 1

        return out


def _id_from_href(href: str) -> Optional[int]:
    """Extrai o id numerico do final do href (ex: /api/v3/projects/42)."""
    if not href:
        return None
    parts = href.rstrip("/").split("/")
    if not parts:
        return None
    last = parts[-1]
    try:
        return int(last)
    except Exception:
        return None
