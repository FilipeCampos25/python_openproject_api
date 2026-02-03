"""
Configuracao central do projeto.

Este arquivo concentra a leitura de variaveis de ambiente e fornece
um objeto simples que o resto do codigo pode consumir.
"""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv, dotenv_values

# Carrega .env do diretorio raiz e backend/.env (se existirem).
BASE_DIR = Path(__file__).resolve().parents[2]
ROOT_ENV = BASE_DIR / ".env"
BACKEND_ENV = BASE_DIR / "backend" / ".env"


def _load_env_files() -> None:
    """Carrega .env e faz backfill de valores vazios no ambiente."""
    for path in (ROOT_ENV, BACKEND_ENV):
        if path.exists():
            load_dotenv(dotenv_path=path, override=False)

    # Backfill com valores nao vazios quando o ambiente estiver vazio.
    merged: dict[str, str] = {}
    for path in (ROOT_ENV, BACKEND_ENV):
        if path.exists():
            for key, value in dotenv_values(path).items():
                if value is not None and value != "":
                    merged[key] = value

    for key, value in merged.items():
        if os.getenv(key) in (None, ""):
            os.environ[key] = value


_load_env_files()


@dataclass
class Settings:
    """Armazena todas as configuracoes do projeto.

    Os valores vem do ambiente para evitar segredos no codigo.
    """

    openproject_base_url: str = os.getenv("OPENPROJECT_BASE_URL", "").strip()
    openproject_username: str = os.getenv("OPENPROJECT_USERNAME", "").strip()
    openproject_password: str = os.getenv("OPENPROJECT_PASSWORD", "").strip()
    # API key do OpenProject (API v3).
    openproject_api_key: str = os.getenv("OPENPROJECT_API_KEY", "").strip()
    # Filtros opcionais para work packages (JSON string compativel com API v3).
    openproject_work_packages_filters_json: str = os.getenv("OPENPROJECT_WORK_PACKAGES_FILTERS_JSON", "").strip()
    api_timeout_seconds: int = int(os.getenv("API_TIMEOUT_SECONDS", "30"))

    export_output_dir: str = os.getenv("EXPORT_OUTPUT_DIR", "./data").strip()
    export_format: str = os.getenv("EXPORT_FORMAT", "csv").strip()

    powerbi_tenant_id: str = os.getenv("POWERBI_TENANT_ID", "").strip()
    powerbi_client_id: str = os.getenv("POWERBI_CLIENT_ID", "").strip()
    powerbi_client_secret: str = os.getenv("POWERBI_CLIENT_SECRET", "").strip()
    powerbi_workspace_id: str = os.getenv("POWERBI_WORKSPACE_ID", "").strip()
    powerbi_dataset_id: str = os.getenv("POWERBI_DATASET_ID", "").strip()
    # Se false, permite conexoes HTTPS com certificados autoassinados (usar com cuidado).
    openproject_verify_ssl: bool = os.getenv("OPENPROJECT_VERIFY_SSL", "true").lower() == "true"


settings = Settings()
