# Configuration

## Visao geral
As configuracoes sao lidas de variaveis de ambiente.
O projeto carrega `.env` na raiz e tambem `backend/.env` (quando existirem).

## Variaveis obrigatorias
- `OPENPROJECT_BASE_URL`
  - URL base do OpenProject (sem `/api/v3` no final).
  - Exemplo: `https://openproject.suaempresa.com`
- `OPENPROJECT_API_KEY`
  - API key do OpenProject (API v3).

## Variaveis opcionais
- `OPENPROJECT_USERNAME` / `OPENPROJECT_PASSWORD`
  - Reservadas para expansao (nao usadas no fluxo atual).
- `OPENPROJECT_WORK_PACKAGES_FILTERS_JSON`
  - Filtro JSON aceito pela API v3 (query param `filters`).
  - Observacao: o `run_api` ignora esse filtro para garantir coleta completa;
    o dashboard usa esse valor quando consulta a API.
  - Exemplo:
    ```
    [{"status":{"operator":"o","values":[]}}]
    ```
- `API_TIMEOUT_SECONDS`
  - Timeout das requisicoes HTTP (default: 30).
- `EXPORT_OUTPUT_DIR`
  - Pasta para arquivos CSV (default: `./data`).
  - Observacao: o caminho e resolvido a partir do diretorio corrente.
- `EXPORT_FORMAT`
  - Formato de exportacao (default: `csv`).
- `OPENPROJECT_VERIFY_SSL`
  - `true` ou `false` para validar certificado SSL (default: `true`).
  - Use `false` apenas se houver certificado autoassinado.

## Power BI (futuro)
As variaveis abaixo estao previstas para integracao via REST API:
- `POWERBI_TENANT_ID`
- `POWERBI_CLIENT_ID`
- `POWERBI_CLIENT_SECRET`
- `POWERBI_WORKSPACE_ID`
- `POWERBI_DATASET_ID`
