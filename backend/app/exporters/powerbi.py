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
