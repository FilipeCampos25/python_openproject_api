# Configuration

## Visao geral
As configuracoes sao lidas de variaveis de ambiente.
O arquivo `.env` e carregado automaticamente pelo `app/config.py`.

## Variaveis obrigatorias
- `OPENPROJECT_BASE_URL`: URL base do OpenProject (sem `/api/v3` no final).
- `OPENPROJECT_API_KEY`: API key do OpenProject (API v3).

## Variaveis opcionais
- `OPENPROJECT_USERNAME` / `OPENPROJECT_PASSWORD`:
  - Reservadas para expansao (nao usadas no fluxo atual).
- `OPENPROJECT_WORK_PACKAGES_FILTERS_JSON`:
  - Filtro JSON aceito pela API v3 (query param `filters`).
  - Exemplo:
    ```
    [{"status":{"operator":"o","values":[]}}]
    ```
- `API_TIMEOUT_SECONDS`:
  - Timeout das requisicoes HTTP (default: 30).
- `EXPORT_OUTPUT_DIR`:
  - Pasta para arquivos CSV (default: `./data`).
- `EXPORT_FORMAT`:
  - Formato de exportacao (default: `csv`).
- `OPENPROJECT_VERIFY_SSL`:
  - `true` ou `false` para validar certificado SSL (default: `true`).

## Power BI (futuro)
As variaveis abaixo estao previstas para integracao via REST API:
- `POWERBI_TENANT_ID`
- `POWERBI_CLIENT_ID`
- `POWERBI_CLIENT_SECRET`
- `POWERBI_WORKSPACE_ID`
- `POWERBI_DATASET_ID`
