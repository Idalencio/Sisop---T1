# Contagem de objetos em matriz binária

Trabalho de Sistemas Operacionais, PUCRS, 2026/2.

**Autor:** Pedro Rocha Idalencio

O programa recebe uma matriz com valores `0` e `1` e conta os grupos de `1`.
Consideramos vizinhos os lados e as diagonais, como pede a conectividade 8.

## Como compilar e executar

É necessário Linux ou macOS com compilador C, `make` e Pthreads. Python 3 é
usado pelos testes e pelo benchmark.

```sh
make clean
make
./bin/conta-objetos-sequencial tests/exemplos/exemplo5.txt
./bin/conta-objetos-paralelo tests/exemplos/exemplo5.txt 4
make test
make benchmark
```

O arquivo de entrada começa com número de linhas e colunas. Depois vêm os
valores da matriz, separados por espaços ou quebras de linha. A versão
paralela recebe também a quantidade de threads. Ela limita esse número ao
número de linhas para não criar faixas vazias.

## Organização e algoritmo

- `src/conta-objetos-sequencial.c`: versão de referência.
- `src/conta-objetos-paralelo.c`: criação das threads e consolidação.
- `src/matriz.c` e `src/flood_fill.c`: leitura da matriz e busca dos grupos.
- `tests/exemplos/`: cinco matrizes do enunciado.
- `tests/validar.py`: confere os resultados dos executáveis.
- `tests/benchmark.py`: mede a versão sequencial e diferentes números de threads.
- `results/`: registros dos testes e das medições.
- `slides/apresentacao.pdf`: slides da apresentação.
- `ROTEIRO_APRESENTACAO.md`: falas sugeridas e perguntas para ensaiar.

As duas versões usam flood fill iterativo. Na paralela, divido a matriz em
faixas de linhas. Cada thread identifica os grupos dentro da própria faixa,
sem escrever nas linhas das outras threads. Depois dos `pthread_join`, a
thread principal compara as duas linhas de cada fronteira, incluindo as
diagonais, e junta os grupos que têm o mesmo objeto. Assim, um objeto que
atravessa várias faixas é contado uma vez. Como essa etapa acontece depois
dos `join`, o Union-Find é alterado por uma única thread.

## Testes e resultados

`make test` verifica as cinco matrizes obrigatórias, casos de fronteira e
diagonais, matrizes pequenas e casos aleatórios. Também confere se entradas
inválidas são recusadas. A referência usada nos testes é independente do
flood fill do programa.

Os cinco resultados pedidos no enunciado são 3, 4, 5, 6 e 7 objetos. O workflow
da aba [Actions](https://github.com/Idalencio/Sisop---T1/actions)
compila, testa e mede o projeto em um runner Linux quando o código muda.
Quando tudo passa na branch `main`, ele atualiza os relatórios em `results/`.
Se um teste falhar, os arquivos parciais ficam como artefato da execução, sem
substituir os últimos resultados aprovados.

O benchmark mede uma matriz maior, com os mesmos dados na versão sequencial
e nas versões paralelas. Faz aquecimento, repete as medições e usa a mediana.
Os resultados salvos em `results/desempenho.md` foram obtidos no GitHub Actions,
em um runner `ubuntu-latest` com quatro CPUs lógicas. As medianas foram 0,02623 s
no sequencial, 0,01518 s com duas threads, 0,01226 s com quatro e 0,01230 s com
oito. Nesse teste, quatro threads tiveram speedup de 2,140x e oito, 2,132x; a
diferença é pequena. É uma única matriz numa máquina virtual hospedada, então
os tempos valem para esse ambiente e não preveem o desempenho em qualquer
computador. O relatório contém as amostras e explica essa limitação.

## Referências e ferramentas

Usei Pthreads e o relógio POSIX `CLOCK_MONOTONIC`. Também usei Python para
automatizar testes e medições. ChatGPT/Codex auxiliaram na implementação,
revisão e preparação dos slides. A ilustração da capa foi gerada com IA. O
código e os resultados precisam ser compreendidos e conferidos pelo autor antes
da apresentação.

