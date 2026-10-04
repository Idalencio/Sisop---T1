# Desempenho medido

Status: **PASSOU**.

Data UTC: 2026-10-04T20:18:57.263514+00:00.

Ambiente declarado: GitHub-hosted runner ubuntu-latest (Linux)

Sistema: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39. CPUs logicas: 4.

Matriz: 1024 x 1024; densidade solicitada 0.45; seed 20260910.

1 aquecimento(s) por configuracao, descartados da mediana; 5 repeticoes medidas.
Ordens alternadas a cada rodada. Todas as contagens concluidas foram comparadas com o primeiro sequencial.

A mediana reduz a influencia de amostras isoladamente lentas. As amostras completas, inclusive
aquecimentos, estao em `desempenho.csv`; hardware, hashes e compilador em `desempenho.json`.

| Configuracao | Threads efetivas | Mediana (s) | Minimo (s) | Maximo (s) | Speedup |
|---|---:|---:|---:|---:|---:|
| Sequencial | 1 fluxo | 0.026225763 | 0.025305388 | 0.026701345 | 1.000 |
| 2 threads | 2 | 0.015177855 | 0.014524369 | 0.017437582 | 1.728 |
| 4 threads | 4 | 0.012257063 | 0.010390507 | 0.014567229 | 2.140 |
| 8 threads | 8 | 0.012298876 | 0.010836483 | 0.013684584 | 2.132 |

Speedup = mediana sequencial / mediana paralela. Valores menores que 1 indicam desaceleracao.
O tempo usado e o campo `Tempo` do programa, que exclui leitura do arquivo e impressao.
O tempo total do processo tambem foi registrado, mas nao entra no calculo do speedup.

Os resultados descrevem esta matriz e este ambiente. Criacao de threads, alocacao, escalonamento,
consolidacao sequencial e disputa por cache/memoria podem superar o ganho do processamento local.
Se a execucao ocorreu em QEMU/TCG ou outra emulacao, os tempos nao representam a escalabilidade
nativa do computador. Emulacao e CPUs virtuais precisam ser declaradas ao apresentar o experimento.
Use a mesma entrada e as mesmas flags ao comparar; nao selecione apenas a melhor amostra.
