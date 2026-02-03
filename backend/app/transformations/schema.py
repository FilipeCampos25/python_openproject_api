# backend/app/transformations/schema.py
"""
Schemas de saida (Power BI-friendly).

Ideia:
- Definir colunas estaveis (e ordem) para cada dataset.
- Assim o Power BI nao "quebra" quando faltarem campos.
"""

from __future__ import annotations

SCHEMAS: dict[str, list[str]] = {
    "projects": [
        "project_id",
        "project_name",
        "project_status",
        "project_href",
        "updated_at",
    ],
    "work_packages": [
        "wp_id",
        "wp_subject",
        "wp_type",
        "wp_status",
        "wp_priority",
        "project_id",
        "project_name",
        "assignee",
        "author",
        "start_date",
        "due_date",
        "done_ratio",
        "created_at",
        "updated_at",
        "is_late",
    ],
}
