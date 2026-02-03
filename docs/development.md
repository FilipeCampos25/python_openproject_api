# Development

## Setup local
1) Crie e ative o virtualenv.
2) Instale dependencias.
3) Configure `.env`.

Comandos (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Padroes de codigo
- Funcoes pequenas e com docstrings.
- Comentarios para explicar regras e decisoes importantes.
- Evitar logica densa sem explicacao.
- Separar coleta, transformacao e exportacao.

## Logging
Use `app/logging_setup.py` para manter um formato unico de log.
Evite prints soltos no meio do pipeline.

## Testes (planejado)
- Unit tests para normalizacao e parsers.
- Integracao para validar a API em ambiente controlado.

## Extensoes comuns
1) **Novo endpoint**:
   - Adicione metodo em `app/openproject_api/client.py`
   - Defina schema em `app/transformations/schema.py`
   - Inclua normalizacao em `app/transformations/normalize.py`
   - Exportar no `app/exporters/powerbi.py`

2) **Novo exporter**:
   - Crie modulo em `app/exporters`
   - Use `normalize_records` antes de exportar

## Troubleshooting rapido
Consulte `docs/troubleshooting.md` para erros comuns.
