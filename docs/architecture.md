# Architecture

## Objetivo
Definir uma arquitetura modular para coleta via API do OpenProject e exportacao para Power BI.
O foco e facilitar manutencao, extensao e depuracao em ambientes reais.

## Componentes
1) **Config (`app/config.py`)**
   - Leitura de variaveis de ambiente.
   - Padroniza caminhos, timeouts e flags (ex: verify SSL).

2) **OpenProject API (`app/openproject_api`)**
   - Cliente HTTP para API v3.
   - Centraliza autenticacao, headers e paginacao.

3) **Transformations (`app/transformations`)**
   - Normaliza dados para schema estavel.
   - Coerce de tipos (datas, inteiros).
   - Campos derivados (ex: `is_late`).

4) **Exporters (`app/exporters`)**
   - Exportacao para CSV (Power BI friendly).
   - Estrutura preparada para novos destinos (REST, Parquet, etc).

5) **Orchestration (`app/orchestration`)**
   - Fluxo end-to-end: coleta -> normaliza -> exporta.
   - Ponto unico para controle do pipeline.

6) **Dashboard (`app/dashboard`)**
   - Visualizacao Streamlit/Plotly.
   - Pode ler via API ou via CSV exportado.

## Fluxo de dados (alto nivel)
```
main.py
  -> orchestration.run_api
       -> openproject_api.client
       -> transformations.normalize
       -> exporters.powerbi
```

## Contratos de dados
Os schemas ficam em `app/transformations/schema.py` e sao aplicados na exportacao.
Isso garante colunas estaveis para evitar quebra no Power BI.

## Dependencias entre camadas
- `orchestration` depende de `openproject_api`, `transformations` e `exporters`.
- `exporters` depende de `transformations` (schema e normalizacao).
- `dashboard` depende de `openproject_api` e `transformations`.

## Erros e resiliencia
- Falhas de API levantam `OpenProjectAPIError`.
- Validacao de filtros JSON falha cedo com mensagem clara.
- Logs consistentes com `logging_setup.py`.

## Extensao recomendada
- Novos endpoints: adicionar metodos no client e atualizar schemas.
- Novas saidas: criar novo exporter e integrar no orchestration.
