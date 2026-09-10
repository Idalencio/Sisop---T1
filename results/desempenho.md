# Desempenho medido

Status: **PASSOU**.

Data UTC: 2026-09-10T21:34:20.810565+00:00.

Ambiente declarado: Alpine Linux 3.24.1 em QEMU TCG x86_64 local, 4 vCPUs, 2 GiB RAM; emulacao, nao desempenho nativo

Sistema: Linux-6.18.35-0-virt-x86_64-with-musl1. CPUs logicas: 4.

Matriz: 1024 x 1024; densidade solicitada 0.45; seed 20260910.

1 aquecimento(s) por configuracao, descartados da mediana; 5 repeticoes medidas.
Ordens alternadas a cada rodada. Todas as contagens concluidas foram comparadas com o primeiro sequencial.

A mediana reduz a influencia de amostras isoladamente lentas. As amostras completas, inclusive
aquecimentos, estao em `desempenho.csv`; hardware, hashes e compilador em `desempenho.json`.

| Configuracao | Threads efetivas | Mediana (s) | Minimo (s) | Maximo (s) | Speedup |
|---|---:|---:|---:|---:|---:|
| Sequencial | 1 fluxo | 0.317325669 | 0.262813266 | 0.595341406 | 1.000 |
| 2 threads | 2 | 0.275011960 | 0.239069914 | 0.421328366 | 1.154 |
| 4 threads | 4 | 0.192030292 | 0.187359316 | 0.361749008 | 1.652 |
| 8 threads | 8 | 0.207392972 | 0.173738357 | 0.381865758 | 1.530 |

Speedup = mediana sequencial / mediana paralela. Valores menores que 1 indicam desaceleracao.
O tempo usado e o campo `Tempo` do programa, que exclui leitura do arquivo e impressao.
O tempo total do processo tambem foi registrado, mas nao entra no calculo do speedup.

Os resultados descrevem esta matriz e este ambiente. Criacao de threads, alocacao, escalonamento,
consolidacao sequencial e disputa por cache/memoria podem superar o ganho do processamento local.
Se a execucao ocorreu em QEMU/TCG ou outra emulacao, os tempos nao representam a escalabilidade
nativa do computador. Emulacao e CPUs virtuais precisam ser declaradas ao apresentar o experimento.
Use a mesma entrada e as mesmas flags ao comparar; nao selecione apenas a melhor amostra.
