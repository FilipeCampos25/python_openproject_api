# OpenProject API Collector

Coleta via API do OpenProject e exportacao para Power BI (CSV).
Este repositorio e um template modular com foco em clareza, extensibilidade e documentacao.

## Visao geral
- **API do OpenProject** para coletar projetos e work packages.
- **Exportacao** para Power BI via CSV (com schema estavel).
- **Modularidade** para evoluir com facilidade (novos endpoints, novos exportadores, novos dashboards).

## Requisitos
- Python 3.10+

## Setup rapido
1) Crie o ambiente virtual
2) Instale dependencias
3) Configure o arquivo `.env`
4) Rode o fluxo

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
cd backend
python -m app.main --mode api
```

## Configuracao (.env)
Variaveis essenciais:
- `OPENPROJECT_BASE_URL`: URL base do OpenProject (ex: https://openproject.suaempresa.com)
- `OPENPROJECT_API_KEY`: API key (API v3)

Variaveis opcionais:
- `OPENPROJECT_WORK_PACKAGES_FILTERS_JSON`: filtros JSON da API v3
- `API_TIMEOUT_SECONDS`: timeout das requisicoes (default: 30)
- `EXPORT_OUTPUT_DIR`: pasta de saida (default: ./data)
- `EXPORT_FORMAT`: formato de exportacao (default: csv)
- `OPENPROJECT_VERIFY_SSL`: true/false para validar SSL (default: true)

Variaveis Power BI (para expansao futura):
- `POWERBI_TENANT_ID`
- `POWERBI_CLIENT_ID`
- `POWERBI_CLIENT_SECRET`
- `POWERBI_WORKSPACE_ID`
- `POWERBI_DATASET_ID`

## Fluxo principal (API)
1) Inicializa cliente OpenProject
2) Coleta projetos
3) Coleta work packages (com filtros opcionais)
4) Normaliza schema
5) Exporta CSVs

## Estrutura
```
.
|-- docs/
|-- backend/
|   |-- app/
|   |   |-- dashboard/
|   |   |-- exporters/
|   |   |-- openproject_api/
|   |   |-- orchestration/
|   |   |-- transformations/
|   |   |-- config.py
|   |   |-- logging_setup.py
|   |   |-- main.py
|-- .env.example
|-- .gitignore
|-- requirements.txt
```

## Documentacao
- `docs/architecture.md`
- `docs/design_philosophy.md`
- `docs/development.md`
- `docs/orchestration.md`
- `docs/configuration.md`
- `docs/troubleshooting.md`

## Executando o dashboard Streamlit (servidor/CI seguro)
O Streamlit pede um e-mail interativamente na primeira execucao se nao houver
`credentials.toml`. Para rodar em servidores/CI sem prompts, use um config local
e aponte `STREAMLIT_CONFIG_DIR`.

- Arquivos no repositorio:
  - `.streamlit/credentials.toml` (email vazio)
  - `.streamlit/config.toml` (headless, enableCORS, port)

- Exemplo local (PowerShell):
```powershell
$env:STREAMLIT_CONFIG_DIR = (Join-Path $PWD '.streamlit')
.\.venv\Scripts\python -m streamlit run backend/app/dashboard/app.py
```

- Exemplo em container/CI (Linux):
```bash
export STREAMLIT_CONFIG_DIR=/workspace/.streamlit
python -m streamlit run backend/app/dashboard/app.py
```

- Seguranca: e seguro versionar `credentials.toml` com `email = ""`. Nao coloque emails pessoais, chaves ou segredos nesses arquivos.

## Autenticacao do dashboard (multiusuario)
- O dashboard usa login/senha persistidos em SQLite local: `backend/data/dashboard_auth.db`.
- No primeiro acesso, a tela do Streamlit pede a criacao do usuario administrador.
- Depois disso, todos os acessos exigem login.
- O administrador consegue criar novos usuarios pela barra lateral do dashboard.

## Smoke test
1) Preencha o `.env` (principalmente `OPENPROJECT_BASE_URL` e `OPENPROJECT_API_KEY`).
2) Rode:

```bash
cd backend
python -m app.main --mode api
```

Se os CSVs forem gerados em `./data`, a conexao via API esta funcionando.

## Atalhos
Para rodar a coleta:
```bash
cd backend
python -m app.main --mode api
```

Para rodar o Streamlit:
```bash
cd backend
python -m streamlit run app/dashboard/app.py
```

## Observacoes
- Este projeto e um template inicial. Ajuste regras de negocio para o seu OpenProject.
- Nunca versione segredos. Use `.env` local.
