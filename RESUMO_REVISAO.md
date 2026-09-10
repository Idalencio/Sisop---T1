# Revisão rápida antes da apresentação

**Objetivo:** contar componentes de células 1 em uma matriz binária,
considerando oito vizinhos. Zero é fundo. Um objeto pode conter muitos
uns, diagonais, curvas e buracos.

**Conectividade 8:** cima, baixo, esquerda, direita e quatro diagonais.
`1 0 / 0 1` forma um objeto. Em conectividade 4 seriam dois.

**Sequencial:** percorre a matriz; encontra 1 sem rótulo; incrementa o
total; executa flood fill; continua. Não conta novamente células rotuladas.

**Flood fill:** pilha dinâmica de índices. Marca a célula ao inseri-la,
retira, examina vizinhos e insere os ainda não visitados. Cada célula
entra no máximo uma vez. Iterativo evita depender de recursão profunda.

**Pthreads:** interface POSIX de threads. As trabalhadoras compartilham
a entrada e o vetor de rótulos, mas executam faixas diferentes. Processo
reúne recursos; thread é um fluxo de execução dentro dele. Concorrência
pode ocorrer em um núcleo; paralelismo exige execução simultânea.

**pthread_create:** inicia uma trabalhadora com ponteiro para seu argumento.
Verificar o código retornado. O argumento precisa continuar válido até
o término. A contagem e o erro ficam na estrutura exclusiva da thread.

**pthread_join:** espera a thread terminar. A principal só consulta
resultados e consolida depois dos joins bem-sucedidos. Join não é mutex.

**Divisão em linhas:** `Tefetiva=min(Tsolicitada,L)`, com solicitação positiva.
`q=L/T`, `r=L%T`; primeiras r faixas recebem q+1 linhas. As demais recebem
q. Intervalo `[inicio,fim)` inclui início e exclui fim. Exemplo: 10 linhas,
3 threads → 4, 3, 3 linhas. A demonstração concorrente usa 2 ou mais.

**Labels/rótulos:** zero é ausência de rótulo. ID da semente:
`linha*C + coluna + 1`, guardado em `size_t`. IDs são únicos e podem ter
saltos. O maior ID não é a quantidade de objetos. Validar dimensões e
alocações impede overflow no cálculo e no espaço para N+1 IDs.

**Componentes locais:** o flood fill nunca sai da própria faixa. Um objeto
global pode gerar vários componentes locais. Somar as contagens locais
sem consolidar produz excesso de contagem.

**Fronteiras:** para cada coluna c da última linha de uma faixa, comparar
com c-1, c e c+1 na primeira linha da faixa seguinte. Verificar limites
e exigir 1 nas duas posições. São exatamente as ligações verticais e
diagonais que podem atravessar a divisão horizontal.

**Union-Find:** parent liga um ID ao pai; raiz aponta para si; find retorna
a raiz; union junta raízes distintas. Compressão encurta caminhos. Rank
orienta uniões equilibradas; após compressão, não é a altura atual exata.
Somente a principal altera essa estrutura, depois dos joins.

**Contagem final:** soma local menos uma unidade por união efetiva de
raízes diferentes. Repetir uma conexão já conhecida não reduz o total.
A-B e B-C implicam A, B e C no mesmo grupo, mesmo em três faixas.

**Race condition:** operações concorrentes disputam um estado sem ordem
correta de acesso. Aqui: entrada só para leitura, rótulos escritos em
faixas disjuntas, pilhas/contagens privadas e principal lendo após joins.
Se o flood fill cruzasse a faixa, essa justificativa seria quebrada.

**Mutex:** exclusão mútua para uma região crítica. Seria necessário em
atualizações concorrentes de estado mutável comum. Não é necessário no
flood fill deste desenho, pois não há disputa de escrita. False sharing
pode prejudicar cache mesmo com posições distintas; não é a mesma coisa
que corrida de dados.

**Deadlock:** espera circular. Trabalhadoras não adquirem mutexes do
algoritmo nem aguardam umas às outras. A principal espera tarefas que
terminam, sem ciclo de espera. Um laço infinito seria outro tipo de bug.

**Complexidade:** N=L*C. Sequencial O(N). Trabalho local total O(N),
podendo aproximar O(N/T) de tempo nessa fase se houver equilíbrio.
Fronteiras: O((T-1)*C) verificações; Union-Find amortizado O(alpha(N))
por operação. Estruturas densas acrescentam custo O(N) sequencial.
Memória total O(N+T). Não prometer tempo total O(N/T).

**Speedup:** `S=Tseq/Tpar`. Acima de 1 acelera; abaixo de 1 desacelera.
Exemplo somente didático: 2 s / 1 s = 2. Na apresentação, usar apenas
os tempos reais registrados nos resultados.

**Overhead:** criação/join, escalonamento, alocações, cache e consolidação.
Pode dominar em matrizes pequenas. Mais threads não garantem mais ganho.
Repetir medições, registrar tempos brutos e explicar a estatística usada.

**Cronômetro:** `clock_gettime(CLOCK_MONOTONIC)` mede tempo decorrido.
Inclui alocações/liberações do processamento, flood fill e, no paralelo,
criação/join e consolidação. Exclui leitura e impressão. Verificar retorno.

**C89 + POSIX:** declarações no início dos blocos; sem variável declarada
no for, sem `//`, sem VLA. Pthreads e o relógio são APIs POSIX. Definir
`_POSIX_C_SOURCE` antes dos includes expõe as declarações necessárias.

**Erros:** conferir entrada, dimensões, alocações e retornos POSIX. Se uma
criação falhar, aguardar as threads já criadas. Não liberar memória que
uma thread de término não confirmado ainda possa acessar.

**Testes:** os cinco resultados oficiais esperados são 3, 4, 5, 6 e 7.
Mostrar somente resultados realmente executados. Comparar versões,
referência independente e casos dirigidos de diagonal/fronteira.

**Três pontos para localizar no código antes de apresentar:** onde a
célula recebe rótulo antes de entrar na pilha; onde cada thread recebe
seu intervalo; onde uma união de raízes distintas decrementa o total.
