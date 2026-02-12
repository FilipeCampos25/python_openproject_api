# Orchestration

## Fluxo principal
1) Valida configuracao (`OPENPROJECT_BASE_URL`, `OPENPROJECT_API_KEY`).
2) Inicializa cliente da API.
3) Coleta projetos.
4) Coleta work packages.
5) Normaliza dados e aplica schema.
6) Exporta CSVs para a pasta configurada.

## Entry point
- `backend/app/orchestration/run_api.py` e o ponto central do fluxo.
- `backend/app/main.py` apenas faz parse de argumentos e chama o orquestrador.

## Inputs
- `.env` com `OPENPROJECT_BASE_URL` e `OPENPROJECT_API_KEY`.
- Timeouts e output dir via `API_TIMEOUT_SECONDS` e `EXPORT_OUTPUT_DIR`.

## Filtros
- O orquestrador ignora `OPENPROJECT_WORK_PACKAGES_FILTERS_JSON` e coleta todos os itens.
- Motivo: garantir dataset completo para exportacao/Power BI.
- O dashboard usa o filtro quando consulta a API.

## Outputs
- `projects.csv`
- `work_packages.csv`

## Onde salva
Os CSVs sao gravados em `EXPORT_OUTPUT_DIR` (default: `./data`, relativo ao diretorio atual).
No fluxo sugerido (`cd backend`), a saida fica em `backend/data`.

## Erros e logs
- Erros de API geram `OpenProjectAPIError` e sao logados.
- Erros de configuracao geram `RuntimeError` com mensagem direta.

## Pontos de extensao
- Adicionar novos endpoints no client e exportar aqui.
- Executar somente etapas especificas (ex: apenas projetos).
- Agendar execucoes (Task Scheduler, cron, etc).
