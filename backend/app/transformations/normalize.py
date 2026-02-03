# backend/app/transformations/normalize.py
"""
Normalizacao de records (list[dict]) para DataFrame.

- Garante schema estavel (colunas e ordem)
- Faz coercion de tipos (datas, numeros)
- Calcula campos auxiliares (ex.: is_late)
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

import pandas as pd

from app.transformations.schema import SCHEMAS


def _ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Garante que todas as colunas existam e ordena."""
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df[columns]


def _coerce_dates(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Converte colunas para date (sem hora)."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df


def _coerce_datetimes(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Converte colunas para datetime."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _coerce_int(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Converte colunas para inteiros (nullable)."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def normalize_records(
    records: Iterable[Mapping[str, Any]],
    schema_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Converte records para DataFrame e aplica normalizacoes uteis.

    - Se schema_name existir em SCHEMAS: garante colunas + ordem
    - Calcula is_late para work_packages quando possivel
    """
    # Permite iteravel/gerador e garante reuso
    records_list = list(records)
    df = pd.DataFrame.from_records(records_list)

    # Se nao veio nada, devolve DF vazio com schema (se conhecido)
    if df.empty and schema_name and schema_name in SCHEMAS:
        return pd.DataFrame(columns=SCHEMAS[schema_name])

    # Normalizacoes por schema
    if schema_name == "projects":
        df = _coerce_datetimes(df, ["updated_at"])

    if schema_name == "work_packages":
        df = _coerce_dates(df, ["start_date", "due_date"])
        df = _coerce_datetimes(df, ["created_at", "updated_at"])
        df = _coerce_int(df, ["wp_id", "project_id", "done_ratio"])

        # is_late: due_date < hoje e done_ratio < 100
        if "due_date" in df.columns:
            today = pd.Timestamp.today().date()
            due = pd.to_datetime(df["due_date"], errors="coerce").dt.date
            done = pd.to_numeric(df.get("done_ratio", 0), errors="coerce")

            is_open = done.fillna(0) < 100
            is_late = (due.notna()) & (due < today) & (is_open)
            df["is_late"] = is_late

    # Aplicar schema estavel se solicitado
    if schema_name and schema_name in SCHEMAS:
        df = _ensure_columns(df, SCHEMAS[schema_name])

    return df
