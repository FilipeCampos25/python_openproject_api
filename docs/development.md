# Development

## Setup local (PowerShell)
1) Crie e ative o virtualenv
2) Instale dependencias
3) Configure `.env`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Rodar o pipeline (API -> CSV)
O entry point esta em `backend/app/main.py`. Execute a partir da pasta `backend`
para manter os caminhos relativos (ex.: `./data`).

```powershell
cd backend
python -m app.main --mode api
```

Saida padrao:
- `backend/data/projects.csv`
- `backend/data/work_packages.csv`

## Rodar o dashboard Streamlit
```powershell
cd backend
python -m streamlit run app/dashboard/app.py
```

Para evitar prompt de email do Streamlit em servidores/CI, use:
```powershell
$env:STREAMLIT_CONFIG_DIR = (Join-Path $PWD '..\.streamlit')
python -m streamlit run app/dashboard/app.py
```

## Padroes de codigo
- Funcoes pequenas e com docstrings.
- Comentarios para explicar regras e decisoes importantes.
- Separar coleta, transformacao e exportacao.
- Evitar logica densa sem explicacao.

## Logging
Use `backend/app/logging_setup.py` para manter um formato unico de log.
Evite prints soltos no meio do pipeline.

## Testes (planejado)
- Unit tests para normalizacao e parsers.
- Integracao para validar a API em ambiente controlado.

## Extensoes comuns
1) **Novo endpoint**:
   - Adicione metodo em `backend/app/openproject_api/client.py`
   - Defina schema em `backend/app/transformations/schema.py`
   - Inclua normalizacao em `backend/app/transformations/normalize.py`
   - Exporte no `backend/app/exporters/powerbi.py`

2) **Novo exporter**:
   - Crie modulo em `backend/app/exporters`
   - Use `normalize_records` antes de exportar

## Dashboard: autenticacao e dados
- Login/senha ficam em SQLite local: `backend/data/dashboard_auth.db`.
- O dashboard salva snapshots CSV em `backend/data` para fallback.
- `OPENPROJECT_WORK_PACKAGES_FILTERS_JSON` e usado no dashboard quando consulta a API.

## Troubleshooting rapido
Consulte `docs/troubleshooting.md` para erros comuns.
