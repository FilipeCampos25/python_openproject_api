# Design Philosophy

## Clareza acima de tudo
Este repositorio prioriza legibilidade. O codigo deve ser simples de entender
por quem chega pela primeira vez.

## Modularidade real
Cada etapa da coleta via API deve estar isolada em seu proprio modulo.
Isso facilita manutencao quando endpoints evoluem.

## Configuracao central
Variaveis sensiveis ou que mudam entre ambientes ficam no `.env`.
Nada de credenciais no codigo.

## Schemas estaveis
Power BI depende de colunas consistentes. Por isso, schemas estao centralizados
e aplicados durante a normalizacao.

## Comentarios uteis
Comentarios devem explicar o "por que" e o "como" quando nao estiver obvio.
Evitar ruido, mas deixar o fluxo didatico.

## Extensibilidade
Novas entidades (ex: work packages, projetos, usuarios) devem virar novos modulos.
Novas saidas (ex: CSV, Parquet, REST) devem virar novos exporters.

## Observabilidade
Logs claros e consistentes em todas as etapas.
