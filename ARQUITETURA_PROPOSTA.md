# Arquitetura escolhida

Plano técnico conferido com as nove páginas do enunciado em 10/09/2026,
antes da implementação. O PDF não impõe um formato de arquivo de entrada;
adotamos dimensões e valores separados por espaços para facilitar os testes.
As matrizes oficiais foram conferidas integralmente.

## Estrutura simples

```text
Makefile
README.md
src/
    matriz.h
    matriz.c
    flood_fill.h
    flood_fill.c
    conta-objetos-sequencial.c
    conta-objetos-paralelo.c
tests/
    exemplos/
    validar.py
    benchmark.py
results/
    resultados.md
    desempenho.csv
EXPLICACAO_COMPLETA.md
PERGUNTAS_APRESENTACAO.md
ROTEIRO_APRESENTACAO.md
RESUMO_REVISAO.md
CHECKLIST_ENUNCIADO.md
slides/
    apresentacao.pdf
```

A biblioteca comum deve conter apenas leitura/alocação e flood fill local.
Union-Find pode ficar no arquivo paralelo se for pequeno. Python, caso
utilizado, fica restrito à automação de testes e medições; os programas
entregues continuam em C89 e Pthreads.

## Dados e identificação

A matriz binária fica em um vetor de bytes de L*C posições. Os rótulos
ficam em outro vetor; 0 representa célula ainda não rotulada/fundo. Para
uma semente na posição (linha, coluna), usar:

`id = linha * C + coluna + 1`

Essa identificação é injetiva: duas células diferentes têm índices
lineares diferentes. Assim, threads não precisam disputar um contador
global. O cálculo só é seguro se a multiplicação L*C, o acréscimo de 1 e
os tamanhos das alocações forem verificados contra overflow de `size_t`.
Se o Union-Find usar N+1 posições, esse acréscimo também deve ser validado.
Não se deve usar `int` sem uma restrição explícita de dimensões.

## Sequencial e flood fill

Percorrer as células; cada 1 sem rótulo inicia um novo componente.
Usar pilha dinâmica de índices lineares. Marcar a célula ao inseri-la na
pilha, evitando inserções duplicadas. Ao removê-la, examinar seus oito
vizinhos válidos. O processamento termina quando a pilha fica vazia.

Cada célula é inserida no máximo uma vez e possui no máximo oito vizinhos:
tempo O(N), espaço adicional O(N), com N=L*C. O flood fill iterativo
evita depender da profundidade limitada da pilha de chamadas.

## Divisão paralela

Com T threads efetivas, usar q=L/T e r=L%T. As primeiras r faixas
recebem q+1 linhas, e as restantes recebem q. Calcular limites acumulados
evita multiplicações desnecessárias. Se a solicitação exceder L, usar no
máximo L threads e informar a quantidade efetiva. Com L=1 só existe uma
faixa útil; o paralelismo real será demonstrado em matrizes com mais linhas.

Cada argumento de thread contém matriz de entrada, vetor de rótulos,
limites da faixa, contagem local e campo de erro. A pilha de trabalho é
privada. O flood fill nunca visita linhas fora da faixa.

## Compartilhamento e sincronização

Durante a identificação local:

- a matriz de entrada é compartilhada somente para leitura;
- o vetor de rótulos é compartilhado, mas as posições escritas são disjuntas;
- a pilha, a contagem e o campo de erro pertencem a uma única thread;
- a thread principal não consulta resultados locais antes dos joins.

Não há necessidade de mutex nessa fase porque nenhum par de threads
escreve na mesma posição nem lê uma posição enquanto outra a modifica.
Compartilhar linhas de cache pode prejudicar desempenho, mas não cria
por si só uma condição de corrida entre objetos distintos.

Verificar `pthread_create` e `pthread_join` pelo código retornado, que
não deve ser confundido com `errno`. Se uma criação falhar, aguardar as
threads já criadas antes de liberar a memória. Se um join falhar e não
for possível garantir que a thread terminou, não liberar memória que ela
ainda possa acessar; tratar essa situação como erro fatal do programa.

## Fronteiras e Union-Find

Após todos os joins bem-sucedidos, iniciar a contagem global com a soma
das contagens locais. Para cada fronteira, examinar os pares de células:

```text
última linha da faixa A:       [c]
primeira linha da faixa B: [c-1] [c] [c+1]
```

Se as duas células forem 1, unir seus rótulos. A estrutura terá `parent`
e tamanho/rank, além de find com compressão de caminho. A união retorna
se realmente fundiu dois conjuntos distintos: somente nesse caso
decrementar a contagem global. Unir repetidamente o mesmo par não pode
reduzir a contagem mais de uma vez.

Uma aresta da conectividade 8 altera a linha em no máximo uma unidade.
Assim, toda ligação que cruza faixas horizontais passa necessariamente
por duas linhas adjacentes na fronteira, com diferença de coluna -1, 0
ou +1. As ligações internas já foram cobertas pelo flood fill. Ao unir
todas as ligações externas, a transitividade do Union-Find reconstrói
exatamente os componentes globais, inclusive os que atravessam várias
faixas. A consolidação será feita apenas pela thread principal.

## Custo e medições

Tempo sequencial: O(N). Trabalho local paralelo: aproximadamente O(N/T)
com equilíbrio de trabalho, mas conteúdo e cache podem causar desequilíbrio.
Há O((T-1)*C) pares de fronteira. Com compressão e união por tamanho/rank,
o custo amortizado de uma operação Union-Find é O(alpha(N)). Uma
alocação/inicialização densa de rótulos e parent pode adicionar O(N)
sequencial e deve constar da análise, sem prometer speedup linear.

Usar `clock_gettime(CLOCK_MONOTONIC, ...)`, verificar retorno e definir
`_POSIX_C_SOURCE` antes dos includes. Isso expõe APIs POSIX sem transformar
a sintaxe do programa em C99. Confirmar a disponibilidade no Linux/macOS
alvo. O intervalo principal deve incluir alocações próprias da solução,
criação/join de threads e consolidação, excluindo leitura/geração e
impressão em ambas as versões. Se houver métricas de fases, identificá-las
separadamente, sem substituir o tempo total comparável.

Executar aquecimento e pelo menos cinco repetições por configuração,
alternando a ordem das configurações. Guardar tempos brutos e usar a
mediana como medida principal. Registrar processador, sistema,
compilador, flags, dimensões, padrão/seed e quantidade efetiva de threads.
Calcular S=Tseq/Tpar; relatar honestamente desaceleração quando S<1.

## Validação prevista

Primeiro executar as cinco matrizes oficiais, já transcritas do PDF.
Depois usar casos dirigidos de fronteira e diagonais, comparar resultados
com uma referência independente simples e testar matrizes pequenas
exaustivamente ou com geração determinística. Testar entrada inválida,
dimensões incompatíveis e excesso de threads. Sanitizers/Valgrind são
verificações adicionais quando disponíveis; resultados só devem ser
marcados como aprovados depois da execução real.
