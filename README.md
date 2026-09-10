# Contagem de objetos com C89 e Pthreads

Trabalho 01 de Sistemas Operacionais, PUCRS, turma 330, 2026/2.
Professor: Filipo Mór.

**Autor:** Pedro Rocha Idalencio. **Matrícula:** preencher.
**Segundo integrante, se houver:** preencher ou remover este campo.

## Problema

Uma matriz binária representa uma imagem: 0 é fundo e 1 é primeiro plano.
Um objeto é um conjunto de células 1 ligadas por lados ou diagonais.
Contamos objetos completos, não a quantidade de células preenchidas.

```text
NW  N  NE
 W  X   E
SW  S  SE
```

Os oito vizinhos de X pertencem à conectividade 8. Por exemplo, as duas
células 1 abaixo formam um único objeto:

```text
1 0
0 1
```

O projeto contém uma implementação sequencial e outra com Pthreads.
Ambas usam flood fill iterativo e produzem a quantidade de objetos.

## Compilação e execução

Requisitos: Linux ou macOS com compilador C, Make e APIs POSIX, incluindo
`clock_gettime(CLOCK_MONOTONIC)`. Python 3 é necessário somente para os
testes e benchmarks automatizados. O código C não usa bibliotecas externas.

Execute no terminal, dentro desta pasta:

```sh
make
./bin/conta-objetos-sequencial tests/exemplos/exemplo5.txt
./bin/conta-objetos-paralelo tests/exemplos/exemplo5.txt 4
make test
make benchmark
```

Para recompilar com verificações mais estritas:

```sh
make clean
make CFLAGS='-O2 -std=c89 -Wall -Wextra -pedantic -Werror -pthread'
```

`make clean` remove apenas os dois executáveis gerados em `bin/`.
Não apaga código, matrizes, resultados ou material de estudo.

O comando de compilação da versão sequencial, sem Make, é:

```sh
mkdir -p bin
cc -O2 -std=c89 -Wall -Wextra -pedantic -pthread src/conta-objetos-sequencial.c src/matriz.c src/flood_fill.c -o bin/conta-objetos-sequencial
```

Para a versão paralela, substitua o fonte principal por
`src/conta-objetos-paralelo.c` e o destino por `bin/conta-objetos-paralelo`.

## Entrada, parâmetros e saída

O arquivo contém L e C, seguidos de exatamente L*C valores 0 ou 1.
Espaços e quebras de linha separam os números. Exemplo:

```text
3 3
1 0 0
0 1 0
0 0 1
```

Aqui a resposta correta é `Objetos: 1`.

- Sequencial: um argumento, o caminho do arquivo.
- Paralelo: caminho do arquivo e número inteiro positivo de threads.
- Se T excede a quantidade de linhas, usamos Tefetivas=min(T,L), sem
  criar faixas vazias. A saída informa a quantidade efetiva.
- T=1 é aceito para comparação e diagnóstico. A demonstração paralela
  do trabalho usa pelo menos duas threads em matrizes com duas ou mais linhas.
- Arquivos incompletos, números inválidos, dimensões nulas, valores fora de
  0/1, tokens excedentes e argumentos inválidos causam erro e código de
  saída diferente de zero.

O programa imprime `Objetos: N` e `Tempo: X s`. O paralelo também imprime
`Threads: T`. O tempo depende da execução e nunca é um valor fixo do exemplo.

## Organização

```text
src/matriz.c, matriz.h                 entrada e relógio POSIX
src/flood_fill.c, flood_fill.h         identificação dentro de uma faixa
src/conta-objetos-sequencial.c          execução sequencial
src/conta-objetos-paralelo.c            threads e consolidação
tests/exemplos/                        cinco matrizes do enunciado
tests/validar.py                       referência independente e testes
tests/benchmark.py                     geração e medições repetidas
results/                              resultados obtidos
slides/apresentacao.pdf                apresentação de até 10 minutos
```

## Versão sequencial

`matriz_ler` carrega a entrada. Um vetor de `size_t` guarda os rótulos,
inicialmente zero. `rotular_faixa` percorre todas as linhas. Cada 1 ainda
sem rótulo inicia um componente e recebe um identificador.

Uma pilha dinâmica guarda os índices das células a visitar. O algoritmo
retira uma célula e insere seus vizinhos preenchidos ainda não rotulados.
A marcação acontece na inserção. Assim, uma célula não entra duas vezes
na pilha. Quando ela esvazia, o componente terminou.

Não há recursão no flood fill. A memória de trabalho cresce no heap,
com verificação de falhas de alocação.

## Versão paralela

Dividimos L linhas em T faixas. Definimos q=L/T e r=L%T. As primeiras
r threads recebem q+1 linhas, e as demais recebem q. Os intervalos usam
início inclusivo e fim exclusivo. Por exemplo, 10 linhas e 3 threads:

| Thread | Intervalo | Linhas processadas |
| --- | --- | --- |
| 0 | [0,4) | 0 a 3 |
| 1 | [4,7) | 4 a 6 |
| 2 | [7,10) | 7 a 9 |

Cada chamada de `pthread_create` inicia um trabalhador que chama
`rotular_faixa` apenas em suas linhas. A thread principal cria todos os
trabalhadores antes de aguardar os resultados com `pthread_join`.

O rótulo de cada componente local é `linha*C + coluna + 1`, usando a
célula que iniciou o flood fill. Esse valor é globalmente único porque
duas posições distintas têm índices lineares diferentes. Zero fica
reservado para ausência de rótulo. A leitura valida os limites de tamanho
antes de calcular produtos ou alocar estruturas, evitando overflow.

## Fronteiras e Union-Find

Somar os totais locais contaria novamente um objeto que atravessa duas
faixas. Depois dos joins, a thread principal examina cada par de faixas
consecutivas. Para a célula de coluna c da linha superior da fronteira,
ela verifica as colunas c-1, c e c+1 da linha inferior, respeitando limites.

`parent` representa conjuntos de componentes equivalentes. `encontrar`
(a operação find) busca a raiz e comprime o caminho. `unir` usa união por rank e
mantém as árvores baixas. Quando duas raízes distintas são unidas, o total
de objetos diminui em um. Uma união repetida não muda o total.

Isso cobre todas as ligações externas: na conectividade 8 a diferença
entre as linhas de duas células vizinhas é no máximo 1. Portanto, uma
aresta que sai de uma faixa necessariamente cruza uma dessas fronteiras
com deslocamento de coluna -1, 0 ou +1. A transitividade das uniões também
trata objetos que atravessam três ou mais faixas.

As linhas verticais laranja do PDF são ilustrativas. Como não dividimos
as colunas, suas conexões permanecem dentro das faixas ou atravessam uma
fronteira horizontal já verificada. Não existe interseção de quatro
faixas horizontais. Os cinco exemplos oficiais continuam obrigatórios.

## Dados compartilhados, corridas e erros

A entrada é compartilhada apenas para leitura. Os rótulos são
compartilhados, mas cada thread escreve exclusivamente nas suas linhas.
Cada trabalhador tem sua própria pilha, contagem local e estado de erro.
Durante a identificação, não lemos rótulos de outra faixa.

Não usamos mutex no flood fill porque não há posições escritas por mais
de uma thread. `pthread_join` estabelece a sincronização antes de a thread
principal ler os resultados e consolidar. O Union-Find só é modificado
pela thread principal. Não há ciclo de aquisição de locks que gere deadlock.

Verificamos retornos de `pthread_create`, `pthread_join`, alocações,
abertura/leitura/fechamento do arquivo e relógio. Os erros de Pthreads são
os códigos retornados pela função, e não necessariamente `errno`. Em
falha de criação, aguardamos todos os trabalhadores que já começaram.
Não liberamos memória que possa estar em uso por uma thread cujo término
não foi confirmado. Uma falha irrecuperável de join encerra o processo.

## Testes

Os cinco arquivos oficiais reproduzem as matrizes das páginas 4 a 6.
Os resultados exigidos são:

| Exemplo | Dimensões | Objetos esperados |
| --- | --- | ---: |
| 1 | 5 x 5 | 3 |
| 2 | 6 x 8 | 4 |
| 3 | 8 x 8 | 5 |
| 4 | 9 x 12 | 6 |
| 5 | 12 x 12 | 7 |

`make test` compara os executáveis entre si e com uma referência Python
independente que une as adjacências do grafo completo. Essa referência
não utiliza flood fill nem particionamento em faixas. Os testes também
incluem diagonais, fronteiras, excesso de threads, divisão com resto,
uma linha, uma coluna, matrizes pequenas exaustivas e casos de seed fixa.
Qualquer divergência ou falha do executável interrompe o teste com erro.

Consulte os arquivos de `results/` para os resultados efetivamente
executados. Valores esperados nesta tabela não são prova de execução.

## Desempenho e complexidade

O relógio monotônico mede o tempo decorrido. `matriz.c` define
`_POSIX_C_SOURCE=200809L` antes de incluir cabeçalhos, expondo as APIs POSIX
necessárias. O código continua usando sintaxe C89, sem VLA, declarações
no `for`, comentários `//` ou recursos C99/C11.

As medições excluem leitura/geração da entrada e impressão. Incluem as
alocações próprias da contagem, o flood fill e a liberação de suas
estruturas. No paralelo, também incluem criação/join, Union-Find e
consolidação. Ambos recebem os mesmos dados.

O benchmark usa aquecimento e medições repetidas. A mediana reduz a
influência de execuções excepcionalmente lentas. Os tempos brutos ficam
em CSV. Calculamos `speedup = mediana_sequencial / mediana_paralela`.
Valor menor que 1 significa desaceleração, e não erro de correção.

Para N=L*C, o flood fill sequencial custa O(N) em tempo e O(N) em espaço.
Com trabalho equilibrado, a identificação local pode se aproximar de
O(N/T). Há O((T-1)*C) pares nas fronteiras. Compressão de caminho e união
por rank tornam as operações Union-Find quase constantes em
média amortizada, O(alpha(N)). Sua inicialização densa adiciona O(N).

Alocação, criação de threads, escalonamento, sincronização, acesso à
memória, cache e consolidação limitam o ganho. Matrizes pequenas costumam
ter pouco trabalho para compensar esse custo. As faixas equilibram linhas,
mas não garantem a mesma quantidade de células preenchidas por trabalhador.

## Resultados obtidos em 10/09/2026

A versão sequencial passou primeiro em 200 execuções. Depois, a suíte
completa passou em **1.305 execuções**, com sequencial e paralelo. Nos cinco
exemplos oficiais, ambas produziram **3, 4, 5, 6 e 7**, respectivamente.
Os registros detalhados estão em `results/validacao.json` e `results/resultados.md`.

Ambiente real de teste: Alpine Linux 3.24.1, GCC 15.2.0, QEMU/TCG local,
4 CPUs virtuais e 2 GiB de RAM. Compilação C89 com `-Werror`, sem warnings.
O Valgrind Memcheck no exemplo 5, sequencial e paralelo com 4 threads,
registrou zero erros e zero bytes alocados ao sair; logs em `results/`.
Isso cobre essas execuções, não constitui prova de ausência de todo bug.
DRD concluiu o exemplo 5 paralelo sem erros não suprimidos. Helgrind
não concluiu por asserção interna; limitações e logs preservados em
`results/AUDITORIA_TECNICA.md`.

Benchmark: matriz 1024 x 1024, densidade 0,45, seed 20260910; um aquecimento
e cinco medições por configuração, em ordem alternada. Mediana:

| Configuração | Tempo (s) | Speedup |
| --- | ---: | ---: |
| Sequencial | 0,317326 | 1,000 |
| 2 threads | 0,275012 | 1,154 |
| 4 threads | 0,192030 | 1,652 |
| 8 threads | 0,207393 | 1,530 |

**São tempos de Linux emulado, não desempenho nativo do computador.**
Quatro threads tiveram a menor mediana nesta amostra. Oito threads para
quatro CPUs virtuais não melhoraram esse resultado. Overhead, escalonamento
e trabalho sequencial são explicações plausíveis, não causas isoladas medidas.
O CSV preserva inclusive amostras lentas. Há variabilidade expressiva;
uma única matriz e cinco repetições não permitem generalizar a aceleração.
Refaça `make benchmark` em Linux nativo para avaliar escalabilidade nativa.

O gerador recria a matriz em `results/matriz-benchmark.txt`; seu SHA-256,
hardware, compilador e hashes dos executáveis estão em `results/desempenho.json`.
Os comandos `make` e `./bin/...` são para um terminal Linux/macOS, não para
PowerShell puro. O Windows não precisa de código alternativo: execute o
mesmo projeto em Linux, WSL configurado ou uma máquina Linux da faculdade.

## Limitações e estudo

O programa guarda a matriz e os rótulos em memória. O paralelo acrescenta
Union-Find e estruturas das threads; matrizes muito grandes podem exceder
a RAM. Não há processamento externo, GPU, pool persistente ou garantia
de aceleração para toda entrada. A compilação final usa C89 com POSIX.

Material para estudar e apresentar:

- `EXPLICACAO_COMPLETA.md`: explicação do zero, algoritmos e conceitos de SO.
- `PERGUNTAS_APRESENTACAO.md`: respostas curtas e completas para a banca.
- `ROTEIRO_APRESENTACAO.md`: fala e demonstração em até 10 minutos.
- `RESUMO_REVISAO.md`: revisão rápida antes da apresentação.
- `CHECKLIST_ENUNCIADO.md`: auditoria requisito por requisito.

## Entrega e referências

Repositório: https://github.com/Idalencio/Sisop---T1

Nesta publicação, os slides foram omitidos a pedido do aluno. A pasta
`slides/` citada na estrutura descreve o material preparado localmente,
não um arquivo disponível neste repositório. O roteiro e os materiais
de estudo em Markdown estão incluídos. A exigência dos slides no enunciado
permanece pendente na entrega pública; o envio no Moodle não foi realizado.

O professor pede um repositório público com fontes, testes, resultados,
documentação e `slides/apresentacao.pdf`. No Moodle deve ser enviado
exclusivamente o endereço do repositório. O prazo confirmado na atividade
é **06/10/2026 às 23h59**. Publicação e envio devem ser conferidos pelo aluno.

- Enunciado do professor: https://moodle.pucrs.br/mod/resource/view.php?id=3903921
- Atividade de entrega: https://moodle.pucrs.br/mod/assign/view.php?id=3903923
- POSIX, criação de threads: https://pubs.opengroup.org/onlinepubs/000095399/functions/pthread_create.html
- POSIX, término e join: https://pubs.opengroup.org/onlinepubs/009695399/functions/pthread_join.html
- POSIX, sincronização de memória: https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html
- Linux, relógios: https://man7.org/linux/man-pages/man3/clock_gettime.3.html

Ferramentas utilizadas: assistência do ChatGPT/Codex para implementação,
revisão e preparação didática; Python para automação de testes e
benchmark; ferramentas de PDF/apresentação para preparar os slides.
O aluno deve revisar, compreender e conseguir explicar o código entregue.
O compilador, sistema e ambiente realmente usados constam nos resultados.
