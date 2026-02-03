# backend/app/orchestration/run_api.py
"""
Orquestracao do fluxo via API do OpenProject.

Sequencia:
1) cria client com OPENPROJECT_BASE_URL + OPENPROJECT_API_KEY
2) coleta projetos
3) coleta work packages (com filtros opcionais)
4) exporta CSVs em EXPORT_OUTPUT_DIR
"""

from __future__ import annotations

from app.config import settings
from app.logging_setup import setup_logging
from app.exporters.powerbi import export_many_to_csv
from app.openproject_api.client import OpenProjectClient, OpenProjectAPIError


def run_api() -> None:
    """Executa o pipeline: coleta via API, normaliza e exporta CSVs."""
    logger = setup_logging()

    # Validacoes basicas de configuracao
    if not settings.openproject_base_url:
        raise RuntimeError("OPENPROJECT_BASE_URL nao configurada no .env")
    if not settings.openproject_api_key:
        raise RuntimeError("OPENPROJECT_API_KEY nao configurada no .env")

    client = OpenProjectClient(
        base_url=settings.openproject_base_url,
        api_key=settings.openproject_api_key,
        timeout=max(10, settings.api_timeout_seconds),
        verify=settings.openproject_verify_ssl,
    )

    logger.info("Iniciando coleta via API. base_url=%s", settings.openproject_base_url)

    # Coleta sem filtros para garantir todos os itens, mesmo se houver filtro no .env
    filters_json = None
    if settings.openproject_work_packages_filters_json.strip():
        logger.warning(
            "Ignorando OPENPROJECT_WORK_PACKAGES_FILTERS_JSON para coletar todos os itens."
        )

    try:
        # Coleta de dados
        projects = client.list_projects()
        logger.info("Projetos coletados: %s", len(projects))

        work_packages = client.list_work_packages(filters_json=filters_json)
        logger.info("Work packages coletados: %s", len(work_packages))

    except OpenProjectAPIError as exc:
        logger.exception("Erro na API do OpenProject: %s", exc)
        raise

    # Exportacao para CSV (schema estavel)
    results = export_many_to_csv(
        {
            "projects": (projects, "projects.csv"),
            "work_packages": (work_packages, "work_packages.csv"),
        }
    )

    for name, path in results.items():
        logger.info("Exportado %s -> %s", name, path)

    logger.info("API concluido.")
