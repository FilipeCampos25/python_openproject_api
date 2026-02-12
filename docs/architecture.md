# Architecture

## Objetivo
Definir uma arquitetura modular para coleta via API do OpenProject, normalizacao e exportacao para Power BI,
com um dashboard Streamlit para visualizacao. O foco e facilitar manutencao, extensao e depuracao em ambientes reais.

## Camadas e responsabilidades
1) **Config (`backend/app/config.py`)**
   - Carrega `.env` da raiz do repositorio e `backend/.env` (se existirem).
   - Centraliza Settings (timeouts, paths, flags e credenciais).

2) **OpenProject API (`backend/app/openproject_api`)**
   - Cliente HTTP para API v3 (`OpenProjectClient`).
   - Autenticacao via Basic Auth com `username="apikey"`.
   - Pagina resultados por `pageSize` e `offset`.

3) **Transformations (`backend/app/transformations`)**
   - `normalize_records` garante schema estavel e coercao de tipos.
   - `schema.py` define colunas fixas para Power BI.
   - Calcula campo derivado `is_late` para work packages.

4) **Exporters (`backend/app/exporters`)**
   - Exporta CSV com encoding `utf-8-sig`.
   - `export_to_powerbi` retorna DataFrames normalizados (uso no dashboard).

5) **Orchestration (`backend/app/orchestration`)**
   - `run_api` valida configuracao, coleta dados, normaliza e exporta.
   - Ignora filtros de work packages para garantir coleta completa.

6) **Dashboard (`backend/app/dashboard`)**
   - Streamlit para visualizacao e analise.
   - Autenticacao local via SQLite (`backend/data/dashboard_auth.db`).
   - Cache local em CSV (snapshot) em `backend/data`.

7) **Logging (`backend/app/logging_setup.py`)**
   - Padroniza formato e nivel de logs no pipeline.

## Fluxo de dados (alto nivel)
```
backend/app/main.py
  -> orchestration.run_api
       -> openproject_api.client
       -> transformations.normalize
       -> exporters.powerbi (CSV)

dashboard/app.py
  -> openproject_api.client (API)
  -> transformations.normalize
  -> UI + cache local (CSV)
```

## Contratos de dados
Os schemas ficam em `backend/app/transformations/schema.py` e sao aplicados na normalizacao e exportacao.
Isso garante colunas estaveis e evita quebra no Power BI.

## Dependencias entre camadas
- `orchestration` depende de `config`, `openproject_api`, `transformations` e `exporters`.
- `exporters` depende de `transformations`.
- `dashboard` depende de `config`, `openproject_api` e `transformations` (nao usa `orchestration`).

## Erros e resiliencia
- Falhas de API levantam `OpenProjectAPIError`.
- Validacoes de configuracao falham cedo com mensagens claras.
- Dashboard usa fallback para ultimo snapshot CSV quando a API falha.

## Extensao recomendada
- **Novo endpoint**: adicionar metodo no client, atualizar schema, normalizacao e exportacao.
- **Nova saida**: criar exporter novo e integrar no orchestration.
- **Novo painel**: estender `DataBundle` e UI no dashboard.
