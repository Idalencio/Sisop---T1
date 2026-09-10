# Resultados de correcao

Status: **PASSOU**. Modo: somente sequencial.

Execucao UTC: 2026-09-10T21:28:18.279471+00:00. Seed: 20260910.

| Exemplo | Dimensoes | Esperado | Sequencial | Paralelo |
|---|---|---:|---:|---|
| 1 | 5 x 5 | 3 | 3 | nao executado |
| 2 | 6 x 8 | 4 | 4 | nao executado |
| 3 | 8 x 8 | 5 | 5 | nao executado |
| 4 | 9 x 12 | 6 | 6 | nao executado |
| 5 | 12 x 12 | 7 | 7 | nao executado |

- 200 execucoes concluidas e registradas em `validacao.json`.
- Referencia independente: Union-Find das adjacencias, sem flood fill ou particionamento.
- Cobertura planejada: 5 exemplos do PDF, 12 casos dirigidos, todas as 64 matrizes 2 x 3,
  100 matrizes aleatorias e entradas invalidas.
- Paralelo: T = 1, 2, 3, 4, 8 e linhas + 5; valores repetidos sao executados uma vez.
- Um resultado PASSOU exige a conclusao de toda a cobertura indicada para o modo selecionado.
