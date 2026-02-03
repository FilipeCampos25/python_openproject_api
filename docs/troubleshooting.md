# Troubleshooting

## Erro: OPENPROJECT_BASE_URL nao configurada
Cause: variavel `OPENPROJECT_BASE_URL` ausente no `.env`.
Solucao: preencher `.env` com a URL base do OpenProject.

## Erro: OPENPROJECT_API_KEY nao configurada
Cause: variavel `OPENPROJECT_API_KEY` ausente no `.env`.
Solucao: gerar API key no OpenProject e adicionar no `.env`.

## Erro: OPENPROJECT_WORK_PACKAGES_FILTERS_JSON invalido
Cause: JSON malformado no filtro.
Solucao: validar o JSON e testar o filtro na UI do OpenProject.

## Erro HTTP 401/403
Cause: API key invalida ou sem permissao.
Solucao: revisar chave, usuario e permissoes.

## Erro HTTP 404/500
Cause: endpoint invalido ou erro do servidor.
Solucao: validar base URL e testar a API diretamente no browser.

## CSV vazio
Cause: filtros muito restritivos ou permissao insuficiente.
Solucao: remover filtros e testar novamente.
