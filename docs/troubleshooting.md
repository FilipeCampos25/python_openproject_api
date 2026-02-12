# Troubleshooting

## Erro: OPENPROJECT_BASE_URL nao configurada
Cause: variavel `OPENPROJECT_BASE_URL` ausente no `.env`.
Solucao: preencher `.env` com a URL base do OpenProject (sem `/api/v3`).

## Erro: OPENPROJECT_API_KEY nao configurada
Cause: variavel `OPENPROJECT_API_KEY` ausente no `.env`.
Solucao: gerar API key no OpenProject e adicionar no `.env`.

## Erro: OPENPROJECT_WORK_PACKAGES_FILTERS_JSON invalido
Cause: JSON malformado no filtro.
Solucao: validar o JSON e testar o filtro na UI do OpenProject.
Observacao: o orquestrador ignora esse filtro; ele impacta apenas o dashboard.

## Erro HTTP 401/403
Cause: API key invalida ou sem permissao.
Solucao: revisar chave, usuario e permissoes.

## Erro HTTP 404
Cause comum: `OPENPROJECT_BASE_URL` com `/api/v3` no final.
Solucao: usar apenas a URL base (ex: `https://openproject.suaempresa.com`).

## Erro HTTP 500
Cause: erro do servidor OpenProject.
Solucao: validar endpoint e testar a API diretamente no browser.

## Erro SSL (CERTIFICATE_VERIFY_FAILED)
Cause: certificado autoassinado.
Solucao: definir `OPENPROJECT_VERIFY_SSL=false` no `.env` (apenas quando necessario).

## CSV vazio
Cause: permissao insuficiente ou base URL incorreta.
Solucao: validar permissao do usuario e testar a API.

## Dashboard pede email ao iniciar
Cause: Streamlit sem `credentials.toml`.
Solucao: setar `STREAMLIT_CONFIG_DIR` apontando para `.streamlit` no repo.

## Dashboard nao autentica
Cause: DB local corrompido ou sem usuario admin criado.
Solucao: remover `backend/data/dashboard_auth.db` e criar o admin novamente.
