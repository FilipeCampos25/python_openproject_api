# Design Philosophy

## Clareza acima de tudo
O repositorio prioriza legibilidade. Codigo e documentacao devem explicar o fluxo
para quem chega pela primeira vez.

## Modularidade real
Cada etapa (coleta, normalizacao, exportacao, visualizacao) vive em seu proprio modulo.
Isso reduz acoplamento e facilita evolucao quando endpoints mudam.

## Configuracao central
Variaveis sensiveis ou que mudam entre ambientes ficam no `.env`.
Nada de credenciais no codigo.

## Schemas estaveis
Power BI depende de colunas consistentes. Schemas estao centralizados
e aplicados durante a normalizacao.

## Fail fast
Erros de configuracao ou API devem falhar cedo, com mensagens claras.
Evita pipelines silenciosos e depuracao lenta.

## Observabilidade pragmatica
Logs claros e consistentes em todas as etapas, sem excesso de ruida.

## Extensibilidade previsivel
Novas entidades viram novos metodos no client + schema + normalizacao.
Novas saidas viram novos exporters.

## Documentacao sincronizada
Docs devem refletir o comportamento real do codigo (paths, defaults e fluxos).
