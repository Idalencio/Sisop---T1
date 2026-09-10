# Sistemas Operacionais — T1

**Pedro Rocha Idalencio**  
PUCRS — 2026/2 — Turma 330

Programa em C89 que conta objetos em uma matriz binária. O valor 0 representa
o fundo e o valor 1 representa parte de um objeto. Células ligadas pelos lados
ou pelas diagonais pertencem ao mesmo objeto (conectividade 8).

## Como executar

É necessário Linux ou macOS com compilador C, Make e suporte a Pthreads e
`clock_gettime`. Python 3 é usado apenas nos testes e no benchmark.
Os comandos abaixo são para um terminal Linux/macOS, dentro da pasta do projeto.

```sh
make
./bin/conta-objetos-sequencial tests/exemplos/exemplo5.txt
./bin/conta-objetos-paralelo tests/exemplos/exemplo5.txt 4
```

O último argumento do paralelo é a quantidade de threads. Se esse número for
maior que a quantidade de linhas, o programa usa uma thread por linha.
A saída informa a quantidade de objetos, o tempo de processamento e, no
paralelo, as threads efetivamente usadas.

A compilação usa `-O2 -std=c89 -Wall -Wextra -pedantic -pthread`.
Para remover os executáveis gerados, use `make clean`.

## Formato da entrada

O arquivo começa com a quantidade de linhas e colunas, seguida dos valores
da matriz. Por exemplo:

```text
3 3
1 0 0
0 1 0
0 0 1
```

Essa matriz tem um objeto, pois as diagonais conectam os três valores 1.
A entrada deve ter exatamente a quantidade indicada de valores, todos 0 ou 1.

## Implementação

O sequencial percorre a matriz. Ao encontrar um 1 ainda não visitado, aumenta
a contagem e usa flood fill para marcar o componente. A busca usa uma pilha
dinâmica, sem recursão. As células são marcadas na inserção na pilha.

O paralelo divide as linhas em faixas. As linhas restantes da divisão são
distribuídas entre as primeiras threads. Cada thread executa o flood fill
somente na sua faixa e gera rótulos usando o índice da semente mais 1.

A matriz de entrada é compartilhada apenas para leitura. Cada thread escreve
nos rótulos da própria faixa e usa pilha e contagem locais. Por isso, não é
necessário mutex durante essa etapa.

Depois dos `pthread_join`, a principal reúne as contagens. Para corrigir
objetos que atravessam faixas, compara cada célula da última linha de uma
faixa com as colunas c-1, c e c+1 da primeira linha da próxima. Union-Find,
com compressão de caminho e união por rank, reúne os rótulos conectados.
A contagem diminui somente quando duas raízes diferentes são unidas.

O sequencial tem tempo O(N), para N células. O trabalho local pode ser
dividido entre as threads, mas as inicializações e a consolidação continuam
sequenciais. A memória total é O(N + T), com T threads. Mais threads não
garantem menor tempo.

Erros de entrada, alocação, relógio e Pthreads são verificados. Se uma criação
falhar, as threads já iniciadas são aguardadas. Uma falha irrecuperável no
join encerra o processo sem liberar buffers que ainda possam estar em uso.

## Organização

- `src/`: implementações sequencial, paralela, leitura e flood fill.
- `tests/`: cinco exemplos do enunciado, validação e benchmark.
- `results/`: registros dos testes, tempos e verificações de memória.
- `Makefile`: compilação e execução dos testes.

## Testes

```sh
make test
```

| Exemplo | Esperado | Sequencial | Paralelo |
| --- | ---: | ---: | ---: |
| 1 | 3 | 3 | 3 |
| 2 | 4 | 4 | 4 |
| 3 | 5 | 5 | 5 |
| 4 | 6 | 6 | 6 |
| 5 | 7 | 7 | 7 |

A suíte completa passou em 1.305 execuções. Inclui os cinco exemplos, casos
de fronteira e diagonal, 64 matrizes 2 x 3, 100 matrizes aleatórias com seed
fixa e entradas inválidas. A referência independente usa as adjacências
da matriz. Os registros estão em `results/validacao.json`.

A compilação também foi verificada com `-Werror`, sem warnings. No exemplo 5,
Valgrind Memcheck não encontrou erros nem vazamentos nas duas versões.
DRD terminou com zero erros não suprimidos no paralelo com quatro threads;
houve 155 ocorrências suprimidas em 50 contextos, sem supressões personalizadas.
Helgrind falhou com uma asserção interna, portanto essa verificação não foi
concluída. Os logs foram mantidos. Falhas de alocação e Pthreads não foram
injetadas artificialmente nos testes.

## Desempenho

```sh
make benchmark
```

Matriz 1024 x 1024, densidade 0,45 e seed 20260910. Foi feito um aquecimento
e cinco medições por configuração, alternando a ordem. A mediana reduz o
peso de execuções isoladamente lentas.

| Configuração | Mediana (s) | Speedup |
| --- | ---: | ---: |
| Sequencial | 0,317326 | 1,000 |
| 2 threads | 0,275012 | 1,154 |
| 4 threads | 0,192030 | 1,652 |
| 8 threads | 0,207393 | 1,530 |

Speedup = tempo sequencial / tempo paralelo. O relógio monotônico mede o
processamento, incluindo alocações, criação/join e consolidação, mas não
a leitura do arquivo nem a impressão.

**Ambiente:** Alpine Linux 3.24.1, GCC 15.2.0, QEMU/TCG, quatro CPUs virtuais
e 2 GiB de RAM. São resultados de emulação, não de desempenho nativo.
Houve variação entre amostras; essa medição não garante a mesma aceleração
em outra máquina ou matriz. Oito threads não melhoraram a mediana neste teste.

Os tempos brutos estão em `results/desempenho.csv`; configuração, seed e
hashes estão em `results/desempenho.json`. A matriz grande é recriada pelo
benchmark. Os scripts também geram relatórios Markdown localmente.

## Observações e referências

O programa mantém a matriz e as estruturas auxiliares na RAM. Não foi
testado em macOS; a execução foi verificada em Linux emulado.

Os slides não estão incluídos neste repositório. O enunciado pede o PDF da
apresentação na entrega final; esse item continua pendente. O link ainda
não foi enviado ao Moodle.

- [Enunciado do trabalho](https://moodle.pucrs.br/mod/resource/view.php?id=3903921)
- [POSIX: pthread_create](https://pubs.opengroup.org/onlinepubs/000095399/functions/pthread_create.html)
- [POSIX: pthread_join](https://pubs.opengroup.org/onlinepubs/009695399/functions/pthread_join.html)
- [clock_gettime](https://man7.org/linux/man-pages/man3/clock_gettime.3.html)

Ferramentas utilizadas: compilador C, Pthreads, Python e Valgrind.
Houve assistência do ChatGPT/Codex na implementação, nos testes e na documentação.
