# Entendendo o T1: contagem de objetos com Pthreads

Leia na ordem. O objetivo é conseguir reconstruir o raciocínio e explicar
as decisões, não decorar frases. Os desenhos pequenos deste material são
exemplos didáticos; as cinco matrizes oficiais ficam nos testes. Resultados
de compilação, correção e desempenho devem ser conferidos nos relatórios
gerados pelas execuções, não inferidos desta explicação.

## 1. O que o programa faz

Uma matriz binária é uma tabela que contém apenas 0 e 1. Neste trabalho,
0 é fundo e 1 é parte de um objeto. Um objeto não precisa ser um retângulo:
pode ser torto, conter buracos e ocupar várias linhas. O que importa é a
existência de um caminho de células 1 vizinhas.

```text
1 1 0 0 0
0 1 0 0 1
0 0 0 0 1
```

Há dois objetos, embora existam cinco células 1. O bloco à esquerda é um
objeto; as duas células à direita formam outro. Portanto, contar os uns
não resolve o problema. Precisamos contar os grupos conectados, também
chamados de componentes conexos.

A entrada começa com L e C, respectivamente a quantidade de linhas e de
colunas, seguida de L*C valores binários. A matriz é guardada em um vetor
contíguo: a posição `(linha, coluna)` corresponde a `linha*C + coluna`.
Essa representação continua sendo uma matriz lógica; muda somente como
os dados ocupam a memória.

## 2. Conectividade 8

Uma célula X pode se conectar a estas oito posições:

```text
NW  N  NE        (-1,-1) (-1,0) (-1,+1)
 W  X   E        ( 0,-1)   X    ( 0,+1)
SW  S  SE        (+1,-1) (+1,0) (+1,+1)
```

As letras representam noroeste, norte, nordeste, oeste, leste, sudoeste,
sul e sudeste. A célula central não é vizinha de si mesma. Nas bordas,
algumas dessas posições não existem e precisam ser ignoradas.

```text
1 0 0
0 1 0
0 0 1
```

Esse desenho tem um objeto em conectividade 8: existe um caminho diagonal
entre os três uns. Em conectividade 4, que considera somente cima, baixo,
esquerda e direita, seriam três objetos. A escolha da conectividade muda
a resposta; considerar as diagonais não é uma otimização opcional.

## 3. Versão sequencial

O programa percorre as células por linhas. Em cada posição pergunta:
“É 1? Ainda está sem rótulo?” Se as duas respostas forem sim, encontrou a
semente de um componente que ainda não foi contado. Então incrementa a
contagem e chama o flood fill para marcar o componente inteiro.

```text
Entrada:           Rótulos depois do processamento:
1 1 0 0            A A 0 0
0 1 0 0            0 A 0 0
0 0 0 1            0 0 0 B
```

O primeiro 1 inicia A e aumenta o total para 1. O flood fill marca os
outros dois uns de A. Quando o percurso externo chega a eles, vê que já
estão marcados e não conta novamente. O último 1 inicia B e aumenta o
total para 2. As letras são didáticas; o programa usa números `size_t`.

O rótulo funciona também como marca de visita. A entrada não precisa ser
destruída para registrar quais células já foram examinadas. A mesma rotina
de contagem local é usada sobre a faixa inteira `[0,L)` no sequencial.

## 4. Flood fill

Flood fill significa expandir uma visita a partir de uma semente. A
estrutura usada é uma pilha dinâmica: o último índice colocado nela é o
primeiro retirado. A pilha fica na memória alocada pelo programa e pode
crescer quando necessário.

O procedimento é:

1. Dar um rótulo à semente e colocá-la na pilha.
2. Retirar um índice enquanto a pilha não estiver vazia.
3. Examinar os oito vizinhos válidos dentro da faixa de trabalho.
4. Para cada vizinho 1 ainda sem rótulo, marcá-lo imediatamente e colocá-lo
   na pilha.
5. Terminar quando não houver mais células aguardando exploração.

Marcar ao inserir é essencial. Se A e B encontram o mesmo vizinho V,
a primeira descoberta já deixa V marcado. A segunda não o insere outra
vez. Marcar somente quando V fosse retirado permitiria várias inserções
antes da primeira retirada.

Por que funciona? A semente pertence ao componente. Cada nova inserção é
uma célula 1 vizinha de uma célula já alcançada, então não sai do componente.
Por outro lado, qualquer caminho de uns pode ser seguido passo a passo
pelas visitas. Ao esvaziar a pilha, todas as células alcançáveis foram
marcadas. Esses dois argumentos mostram que o flood fill marca exatamente
o componente da semente.

Para N=L*C, a varredura total e as visitas custam O(N): cada célula é
inserida no máximo uma vez e tem no máximo oito vizinhos. A pilha pode
ocupar O(N) no pior caso, assim como os rótulos. A versão iterativa evita
uma chamada recursiva por avanço do caminho e a dependência da pequena
pilha de chamadas da thread. Ela ainda pode ficar sem memória; por isso
as alocações são verificadas.

## 5. Threads

Um processo é uma execução de um programa com seus recursos, como espaço
de endereçamento e arquivos abertos. Uma thread é um fluxo de execução
dentro de um processo. As threads compartilham a memória do processo, mas
cada uma tem sua própria execução, registradores e pilha de chamadas.

Concorrência significa que tarefas progridem no mesmo intervalo de tempo,
possivelmente alternadas em um único núcleo. Paralelismo significa executar
ao mesmo tempo, por exemplo em núcleos diferentes. Criar quatro threads
permite paralelismo, mas não garante quatro núcleos disponíveis nem uma
aceleração de quatro vezes.

Pthreads é a interface de threads POSIX utilizada diretamente neste
trabalho. `pthread_create` inicia uma thread e recebe, entre outros dados,
a função de trabalho e um ponteiro para seu argumento. O argumento aponta
para uma estrutura que continua existindo até a thread terminar; não se
deve passar o endereço de uma variável de laço reutilizada como se fosse
um argumento exclusivo de cada thread.

A estrutura contém a entrada compartilhada, o vetor de rótulos, os limites
da faixa, o resultado local e a informação de erro. A rotina de trabalho
preenche seu resultado e termina. A resposta numérica fica nessa estrutura,
não depende de converter um inteiro em ponteiro no retorno da thread.

`pthread_join` espera uma thread específica terminar. Depois dos joins
bem-sucedidos, a principal pode consumir os resultados produzidos e iniciar
a consolidação. A função de trabalho retorna um `void *`; neste desenho
não precisamos usar esse retorno para transportar a contagem.

Tanto `pthread_create` quanto `pthread_join` retornam zero no sucesso ou
um código de erro. Esse código deve ser examinado diretamente; não é
correto assumir que ele estará em `errno`.

## 6. Divisão do trabalho

As linhas são divididas em faixas contíguas e não sobrepostas. A notação
`[inicio,fim)` inclui inicio e exclui fim. Assim `[0,3)` são as linhas
0, 1 e 2. A linha 3 pertence à próxima faixa.

```text
12 linhas, 4 threads efetivas

Thread 0: [0,3)    -> linhas 0, 1, 2
-----------------------------------
Thread 1: [3,6)    -> linhas 3, 4, 5
-----------------------------------
Thread 2: [6,9)    -> linhas 6, 7, 8
-----------------------------------
Thread 3: [9,12)   -> linhas 9, 10, 11
```

Se T é a quantidade efetiva, calculamos `q=L/T` e `r=L%T`. As primeiras
r threads recebem q+1 linhas. As demais recebem q. Por exemplo, L=10 e
T=3 produzem tamanhos 4, 3 e 3: `[0,4)`, `[4,7)` e `[7,10)`.

O programa aceita uma quantidade solicitada positiva e limita a efetiva
a `min(Tsolicitada,L)`. Não faz sentido criar uma faixa sem nenhuma linha.
Uma thread é útil para comparar o algoritmo, mas a demonstração de
paralelismo deve incluir pelo menos duas threads efetivas.

Equilibrar linhas não garante equilibrar todo o trabalho: uma faixa pode
ter muitos uns conectados e outra apenas fundo. A divisão escolhida é
simples, previsível e deixa fácil identificar as fronteiras.

## 7. Componentes locais

Cada thread executa o flood fill somente dentro da própria faixa. Um
vizinho fora de `[inicio,fim)` não pode ser visitado, mesmo que seja 1.
Isso permite que as threads trabalhem independentemente.

O componente local é um grupo conectado quando olhamos apenas aquela
faixa. Um componente global pode aparecer como vários componentes locais.
Até dois grupos separados dentro da mesma faixa podem se conectar por
um caminho que sai dela e volta. A consolidação resolverá ambos os casos.

Cada thread encontra componentes de verdade na sua região; não fica
somente esperando ou dividindo uma contagem calculada previamente pela
thread principal. É nessa identificação local que ocorre o trabalho
concorrente principal.

## 8. Problema das fronteiras

Considere dois recortes, um em cada faixa:

```text
1       componente local A
-----   fronteira
1       componente local B
```

Cada thread conta 1. Somar daria 2, mas os uns são vizinhos verticais:
globalmente existe um objeto. O mesmo acontece na diagonal:

```text
1 0     componente local A
-----   fronteira
0 1     componente local B
```

Também existe um objeto em conectividade 8. Uma consolidação que olhasse
somente a mesma coluna falharia no segundo desenho.

O problema não é um erro do flood fill local: ele respeitou corretamente
seus limites. Falta apenas registrar quais componentes locais pertencem
ao mesmo componente global.

## 9. Matriz de rótulos

Há dois vetores diferentes: o binário responde “é fundo ou primeiro plano?”;
o de rótulos responde “qual componente local visitou esta célula?”. Rótulo
zero significa sem rótulo; no fim, o fundo continua com zero.

Para a semente `(linha,coluna)`, o identificador é:

```text
id = linha*C + coluna + 1
```

Em uma matriz com 4 colunas, as sementes `(0,0)`, `(1,2)` e `(3,1)` geram
1, 7 e 14. Os IDs não precisam ser consecutivos e não representam a
quantidade de objetos. O acréscimo de 1 reserva zero para ausência de rótulo.

Sementes diferentes geram IDs diferentes porque o índice linear é único
para cada célula. Como faixas não compartilham células, threads diferentes
também não escolhem a mesma semente. Isso dispensa um contador global de
IDs com mutex.

A segurança depende de validar dimensões e tamanhos: L*C e alocações com
`sizeof(size_t)` não podem estourar o tipo. A estrutura Union-Find também
precisa de N+1 posições para usar o ID N. Rótulos usam `size_t`, o tipo
apropriado para tamanhos e índices de memória.

## 10. Union-Find

Union-Find mantém grupos de identificadores considerados equivalentes.
Ele não procura pixels na matriz. Recebe a informação “estes dois rótulos
estão conectados” e organiza as equivalências.

`parent[x]` informa o pai de x em uma árvore de representantes. Uma raiz
é um elemento cujo pai é ele mesmo. No início, cada ID válido representa
seu próprio grupo:

```text
parent[1]=1     parent[7]=7     parent[14]=14
```

No fonte, `encontrar` implementa find e `unir` implementa union.
`find(x)` sobe pelos pais até encontrar a raiz do grupo de x. Se
`find(a)==find(b)`, os dois IDs já pertencem ao mesmo grupo.

`union(a,b)` primeiro encontra as raízes. Se forem diferentes, conecta
uma árvore à outra; se forem iguais, não precisa mudar a estrutura.

```text
union(1,7):          7 -> 1
union(7,14):       14 -> 1     e     7 -> 1

find(1)=find(7)=find(14)=1
```

Os números e a direção das setas são ilustrativos. Qual raiz vence pode
mudar conforme o rank; a equivalência e a contagem continuam as mesmas.

Compressão de caminho faz os elementos encontrados durante `find`
apontarem mais diretamente para a raiz. Por exemplo:

```text
Antes:  14 -> 7 -> 1
Depois: 14 ------> 1     e     7 -> 1
```

União por rank evita pendurar uma árvore de rank maior sob uma de rank
menor. Quando os ranks são iguais, escolhe uma raiz e aumenta seu rank.
Depois da compressão, rank não é necessariamente a altura atual exata;
ele continua sendo uma informação usada para manter as uniões equilibradas.

Nesta implementação, Union-Find é usado somente pela thread principal,
depois dos joins. Portanto, suas alterações de `parent` e `rank` não
precisam de sincronização entre várias threads.

## 11. Consolidação

Para cada par de faixas consecutivas, o programa olha a última linha da
faixa de cima e a primeira da faixa de baixo. Para cada coluna c:

```text
Faixa A:                    superior[c]
                              / | \
Fronteira: ------------------------------------------------
Faixa B:             inferior[c-1] [c] [c+1]
```

Somente posições dentro da matriz são consideradas. Se o par de células
é 1/1, seus rótulos são unidos. Células de fundo não geram equivalências.

Por que isso é suficiente? Podemos imaginar um grafo: cada célula 1 é um
vértice, e cada par de vizinhos da conectividade 8 é uma aresta. Toda
aresta é de um destes dois tipos:

1. Interna a uma faixa: foi coberta pelo flood fill daquela thread.
2. Entre faixas: como a diferença de linha de dois vizinhos é no máximo
   1, precisa ligar justamente as duas linhas adjacentes de uma fronteira.
   A diferença de coluna só pode ser -1, 0 ou +1.

Logo, não existe outra forma de uma aresta atravessar uma faixa horizontal.
Processar todos esses pares cobre todas as arestas externas, incluindo
diagonais. As uniões são transitivas, então um objeto atravessando três,
quatro ou mais faixas também é reconstruído.

## 12. Contagem final

Começamos com a soma das contagens locais. Essa é a quantidade de grupos
antes de conhecer as equivalências externas. Cada união que junta duas
raízes diferentes reduz a quantidade de grupos em exatamente 1.

```text
Locais: A, B, C                     total = 3
união A-B: eram grupos distintos    total = 2
união B-C: eram grupos distintos    total = 1
união A-C: já estavam unidos        total = 1
```

Por isso não basta testar se os rótulos numéricos são diferentes. A e C
podem ter números diferentes e já pertencer à mesma raiz. A operação de
união informa se realmente fundiu dois conjuntos; só nesse caso o total
é decrementado.

Isso evita contar uma mesma conexão várias vezes em fronteiras largas.
Também dispensa percorrer novamente toda a matriz para reescrever os
rótulos globais. Os rótulos continuam locais; o Union-Find guarda a
equivalência, e a variável total guarda a quantidade final de objetos.

## 13. Race conditions

Uma condição de corrida aparece quando operações concorrentes sobre um
estado compartilhado dependem de uma ordem de execução que não foi
controlada. Em um incremento compartilhado, por exemplo, duas threads
podem ler o mesmo valor, calcular o mesmo sucessor e perder uma atualização.
Em C/Pthreads, acessos conflitantes sem a sincronização necessária também
podem constituir uma corrida de dados; não se deve tratá-los como apenas
um resultado ocasionalmente errado.

Nosso desenho separa quem escreve o quê:

| Dado | Uso durante a identificação local |
| --- | --- |
| Matriz binária | Todas as threads leem; nenhuma modifica |
| Rótulos da faixa 0 | Somente a thread 0 escreve e consulta |
| Rótulos da faixa 1 | Somente a thread 1 escreve e consulta |
| Pilha de uma thread | Somente aquela thread utiliza |
| Contagem e erro de uma thread | A própria thread escreve; a principal lê após join |
| Parent e rank | Somente a principal, depois de todos os joins |

```text
labels[linhas 0..2]  <- thread 0
labels[linhas 3..5]  <- thread 1
labels[linhas 6..8]  <- thread 2
```

O vetor é compartilhado, mas suas posições de escrita não são. O flood
fill deve respeitar a faixa também ao examinar vizinhos; permitir que
avance para outra faixa quebraria essa justificativa.

Posições distintas podem ocupar a mesma linha de cache. Isso pode gerar
contenção de cache, conhecida como false sharing, mas não significa que
as threads escreveram no mesmo objeto de memória.

## 14. Mutex

Mutex é um mecanismo de exclusão mútua: somente uma thread por vez pode
entrar na região protegida por aquele mutex. Seria necessário, por exemplo,
se várias threads atualizassem diretamente um contador global comum ou
alterassem simultaneamente a mesma estrutura Union-Find.

Neste programa, cada thread produz sua contagem local e usa uma região
exclusiva de rótulos. A principal agrega os resultados depois dos joins.
Assim, não existe estado mutável disputado no flood fill que precise de
um mutex. Colocar um mutex em toda visita acrescentaria custo sem resolver
um conflito que o desenho já eliminou.

`pthread_join` e mutex não são a mesma coisa. Join espera o término de uma
thread. Mutex controla o acesso concorrente a uma região durante a
execução. Aqui usamos a separação de dados e joins para organizar as fases.

## 15. Deadlock

Deadlock é uma espera circular que impede as tarefas de avançar. Um
exemplo clássico: A segura o mutex X e espera Y; B segura Y e espera X.
Nenhuma pode liberar o que a outra aguarda.

O fluxo normal deste programa não forma esse ciclo. As trabalhadoras não
adquirem mutexes do algoritmo nem fazem join umas nas outras. Elas apenas
terminam o trabalho de sua faixa; a principal espera suas conclusões.
Portanto, não há espera circular nesse protocolo.

Isso não prova que qualquer bug seria impossível: um laço que não termina
poderia deixar a principal esperando indefinidamente, e isso precisa ser
investigado. Laço infinito e deadlock não são conceitos idênticos.

Se uma criação falhar, é necessário aguardar as threads já iniciadas antes
de liberar dados que possam continuar usando. Se um join falhar, não se
pode presumir que a thread terminou e liberar a memória compartilhada como
se houvesse sucesso. Esses caminhos de erro também fazem parte do desenho.

## 16. Complexidade

Considere L linhas, C colunas, N=L*C células e T threads efetivas.

O sequencial varre N posições e visita cada célula 1 no máximo uma vez,
com até oito vizinhos. Portanto, o tempo é O(N). Entrada, rótulos e pilha
ocupam O(N) memória no pior caso.

No paralelo, o trabalho total de identificação local continua O(N). Se
as faixas demandarem esforços parecidos e houver recursos de execução,
o tempo dessa fase se aproxima de O(N/T). Isso descreve uma fase sob
hipóteses de equilíbrio, não uma garantia de tempo total do programa.

Há T-1 fronteiras. Cada uma tem C colunas e até três pares por coluna,
portanto há O((T-1)*C) verificações externas. Com compressão de caminho e
união por rank, find/union têm custo amortizado O(alpha(N)), em que alpha
é a função inversa de Ackermann, de crescimento extremamente lento.

Uma expressão útil para o tempo da solução é:

```text
alocações/inicializações + criação/join
+ máximo do trabalho local de uma faixa
+ consolidação das fronteiras
```

Rótulos e Union-Find são estruturas densas: alocar/inicializar o estado
proporcional a N pode introduzir O(N) fora da fase paralela. A consolidação
também é sequencial. Logo, não se deve afirmar que o tempo total é sempre
O(N/T), nem prometer speedup linear.

A memória total permanece O(N+T): a soma das capacidades necessárias das
pilhas locais é proporcional às células das faixas, além dos vetores de
entrada, rótulos, parent/rank e das estruturas das threads. Não há uma
cópia completa da matriz para cada thread.

## 17. Speedup

Speedup compara o tempo da referência sequencial com o da versão paralela:

```text
S = Tseq / Tpar
```

Se, em um exemplo hipotético, Tseq=2 s e Tpar=1 s, então S=2: a versão
paralela levou metade do tempo. Se Tpar=4 s, S=0,5: o paralelo ficou mais
lento. Esses números explicam a fórmula; não são resultados do trabalho.

Para os resultados reais, use a mesma matriz, as mesmas condições e a
mesma definição de trecho cronometrado. Faça várias execuções e registre
os tempos brutos. A mediana é uma escolha útil porque sofre menos com
uma execução isolada muito lenta causada por outra atividade da máquina.

O intervalo medido inclui alocações próprias do processamento, flood
fill, liberação dessas estruturas e, no paralelo, criação/join e
consolidação. A leitura da entrada e a impressão ficam fora. Não seria
uma comparação justa incluir trabalho de preparação em uma versão e
excluí-lo da outra.

Mais threads não dão aceleração infinita. A parte sequencial limita a
melhoria, os núcleos são finitos e a memória tem largura de banda limitada.
Para uma fração sequencial s, o modelo ideal de Amdahl limita a aceleração
a `1/(s + (1-s)/T)`; custos adicionais podem piorar o resultado real.

## 18. Overhead

Overhead é trabalho adicional necessário para organizar uma solução. Na
versão paralela, criar threads, escaloná-las, aguardar joins e consolidar
fronteiras custa tempo que o sequencial não paga da mesma forma.

O escalonador decide quando cada thread executa. Muitas threads disputando
poucos núcleos podem aumentar trocas de execução. O acesso concorrente à
memória pode disputar largura de banda; os caches ajudam a reduzir acessos
mais caros, mas seu comportamento depende do padrão de acesso. Alocação
das pilhas também custa e pode disputar recursos internos do alocador.

Em uma matriz pequena, o flood fill termina rapidamente e esses custos
podem dominar. Em uma matriz maior pode existir trabalho suficiente para
compensá-los, mas o tamanho sozinho não garante speedup: o padrão dos
objetos, o hardware e a quantidade de faixas importam.

Por isso, resultados menores que 1 não devem ser escondidos. Apresente os
tempos reais e explique a relação entre trabalho útil, preparação e trecho
sequencial. Uma hipótese de desempenho é uma interpretação; não substitui
a medição.

## 19. C89

C89/C90 define a versão da linguagem C usada nos fontes. Algumas formas
comuns em C mais recente não são permitidas nesta entrega:

```c
/* Forma compatível com C89: declaração no início do bloco. */
int i;
for (i = 0; i < 10; i++) {
    /* trabalho */
}
```

Não usamos declaração dentro do `for`, comentários `//`, arrays de tamanho
variável (VLA) nem recursos que dependam de C99/C11. Variáveis são declaradas
no início dos blocos; memória cujo tamanho depende da entrada é alocada
dinamicamente.

`size_t` já existe em C89. Entretanto, a conversão de impressão `%zu` só
foi padronizada posteriormente; imprimir um tipo de tamanho exige cuidado
para manter formato e argumento compatíveis. A compilação usa as opções
`-std=c89 -Wall -Wextra -pedantic -pthread` para exigir a linguagem e
avisar sobre problemas detectáveis pelo compilador.

Compilar sem warnings é um bom sinal, mas não prova contagem correta nem
ausência de erro de memória. Por isso precisamos também dos testes e das
verificações de execução disponíveis.

## 20. POSIX

POSIX é uma família de especificações de interfaces de sistemas
operacionais. Ela permite escrever programas com interfaces comuns em
ambientes como Linux e macOS. Pthreads é a interface POSIX usada para
trabalhar com threads.

C89 descreve a linguagem; POSIX descreve interfaces de sistema utilizadas
pelo programa. Portanto, usar Pthreads e `clock_gettime` não significa
automaticamente usar sintaxe de C99. Significa que, além de um compilador
C compatível, precisamos de uma plataforma POSIX que ofereça essas APIs.

A macro `_POSIX_C_SOURCE` é definida antes dos includes para solicitar
que os cabeçalhos exponham as declarações POSIX necessárias. Isso não
cria uma função ausente em um sistema antigo; a plataforma alvo precisa
realmente fornecê-la.

O relógio escolhido é `CLOCK_MONOTONIC`, consultado por `clock_gettime`.
Ele é apropriado para intervalos porque não acompanha ajustes do relógio
de calendário. Não é uma medida de consumo de CPU: mede o tempo decorrido
da operação, incluindo o período em que a execução eventualmente não
estava no processador. A chamada pode falhar, então seu retorno também
é verificado.

Para apresentar com segurança, localize nos fontes onde começa e termina
a medição, onde as threads são criadas e aguardadas e onde a contagem é
reduzida por uma união efetiva. Esses três pontos conectam os conceitos
ao comportamento concreto do programa.
