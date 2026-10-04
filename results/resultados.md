# Resultados de correcao

Status: **PASSOU**. Modo: sequencial e paralelo.

Execucao UTC: 2026-10-04T20:18:55.977660+00:00. Seed: 20260910.

| Exemplo | Dimensoes | Esperado | Sequencial | Paralelo |
|---|---|---:|---:|---|
| 1 | 5 x 5 | 3 | 3 | T1: 3; T2: 3; T3: 3; T4: 3; T8: 3; T10: 3 |
| 2 | 6 x 8 | 4 | 4 | T1: 4; T2: 4; T3: 4; T4: 4; T8: 4; T11: 4 |
| 3 | 8 x 8 | 5 | 5 | T1: 5; T2: 5; T3: 5; T4: 5; T8: 5; T13: 5 |
| 4 | 9 x 12 | 6 | 6 | T1: 6; T2: 6; T3: 6; T4: 6; T8: 6; T14: 6 |
| 5 | 12 x 12 | 7 | 7 | T1: 7; T2: 7; T3: 7; T4: 7; T8: 7; T17: 7 |

- 1319 execucoes concluidas e registradas em `validacao.json`.
- Referencia independente: Union-Find das adjacencias, sem flood fill ou particionamento.
- Cobertura planejada: 5 exemplos do PDF, 14 casos dirigidos, todas as 64 matrizes 2 x 3,
  100 matrizes aleatorias e entradas invalidas.
- Paralelo: T = 1, 2, 3, 4, 8 e linhas + 5; valores repetidos sao executados uma vez.
- Um resultado PASSOU exige a conclusao de toda a cobertura indicada para o modo selecionado.
