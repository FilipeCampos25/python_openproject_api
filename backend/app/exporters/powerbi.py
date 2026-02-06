# backend/app/exporters/powerbi.py
"""
Exportacao para Power BI (principalmente via CSV).

Objetivo:
- Receber records (list[dict])
- Normalizar para um schema estavel (para o Power BI nao quebrar)
- Exportar em CSV com encoding amigavel (utf-8-sig)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from app.config import settings
from app.openproject_api.client import OpenProjectClient, OpenProjectAPIError
from app.transformations.normalize import normalize_records


def export_to_csv(
    records: Iterable[Mapping[str, Any]],
    filename: str,
    schema_name: Optional[str] = None,
) -> Path:
    """
    Exporta `records` para CSV no diretorio configurado.

    Args:
        records: iteravel de dicts.
        filename: ex. "projects.csv"
        schema_name: se fornecido, aplica um schema conhecido (ex.: "projects", "work_packages")

    Returns:
        Caminho do arquivo gerado.
    """
    output_dir = Path(settings.export_output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Normaliza registros para garantir colunas estaveis
    df = normalize_records(records, schema_name=schema_name)

    out_path = output_dir / filename
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


def export_many_to_csv(
    datasets: dict[str, tuple[Iterable[Mapping[str, Any]], str]],
) -> dict[str, Path]:
    """
    Exporta multiplos datasets para CSV.

    Formato:
      datasets = {
        "projects": (records, "projects.csv"),
        "work_packages": (records, "work_packages.csv"),
      }
    """
    results: dict[str, Path] = {}
    for schema_name, (records, filename) in datasets.items():
        results[schema_name] = export_to_csv(records, filename, schema_name=schema_name)
    return results


def export_to_powerbi(
    base_url: str,
    api_key: str,
    verify_ssl: bool = True,
    timeout: Optional[int] = None,
) -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """
    Coleta dados via API do OpenProject e retorna DataFrames normalizados.

    Essa funcao e usada pelo dashboard (modo "api").
    """
    # Import local para evitar dependencia pesada no import do modulo
    import pandas as pd

    if not base_url:
        raise RuntimeError("OPENPROJECT_BASE_URL nao configurada no .env")
    if not api_key:
        raise RuntimeError("OPENPROJECT_API_KEY nao configurada no .env")

    client = OpenProjectClient(
        base_url=base_url,
        api_key=api_key,
        timeout=timeout or max(10, settings.api_timeout_seconds),
        verify=verify_ssl,
    )

    try:
        projects = client.list_projects()
        work_packages = client.list_work_packages(filters_json=None)
    except OpenProjectAPIError:
        raise

    projects_df = normalize_records(projects, schema_name="projects")
    work_packages_df = normalize_records(work_packages, schema_name="work_packages")

    return projects_df, work_packages_df
