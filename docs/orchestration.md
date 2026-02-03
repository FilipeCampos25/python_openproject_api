# Orchestration

## Fluxo principal
1) Inicializa cliente da API (base URL + API key).
2) Coleta projetos.
3) Coleta work packages (com filtros opcionais).
4) Normaliza dados e aplica schema.
5) Exporta CSVs para pasta configurada.

## Entry point
- `backend/app/orchestration/run_api.py` e o ponto central do fluxo.
- `backend/app/main.py` apenas faz parse de argumentos e chama o orquestrador.

## Inputs
- `.env` com `OPENPROJECT_BASE_URL` e `OPENPROJECT_API_KEY`.
- Filtros opcionais em `OPENPROJECT_WORK_PACKAGES_FILTERS_JSON`.

## Outputs
- `projects.csv`
- `work_packages.csv`

## Pontos de extensao
- Adicionar novos endpoints no client e exportar aqui.
- Executar somente etapas especificas (ex: apenas projetos).
- Agendar execucoes (Task Scheduler, cron, etc).
