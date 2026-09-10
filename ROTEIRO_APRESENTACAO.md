# Roteiro de apresentação — até 10 minutos

Os intervalos abaixo são uma distribuição planejada da fala, não medições
de desempenho. Ensaie com um relógio. Deixe abertos os fontes, os testes
e os resultados reais. No trecho de resultados, leia os valores produzidos
pelo projeto; nunca substitua uma execução pendente por um número estimado.

## 0:00–1:00 — Problema

“O trabalho conta objetos em uma matriz binária. Zero representa fundo e
um representa parte de um objeto. Não queremos saber quantos uns existem,
mas quantos grupos conectados eles formam.

A conectividade é 8: cada posição considera os vizinhos horizontais,
verticais e diagonais. Neste desenho, os dois uns formam um objeto,
porque se tocam na diagonal.”

Mostre:

```text
1 0
0 1
```

“Implementei uma solução sequencial e outra com Pthreads. Ambas usam a
mesma definição de vizinhança. A principal dificuldade do paralelo é
reconhecer quando pedaços encontrados por threads diferentes pertencem
ao mesmo objeto.”

## 1:00–3:00 — Sequencial e flood fill

“A versão sequencial percorre a matriz por linhas. Quando encontra um 1
sem rótulo, inicia um componente e aumenta a contagem. O flood fill visita
todos os uns alcançáveis a partir dessa semente.

Uso uma pilha dinâmica de índices. Coloco a semente, retiro uma posição,
examino seus oito vizinhos válidos e insiro os uns ainda não visitados.
A célula é marcada na inserção na pilha, antes da próxima visita. Mesmo que dois
caminhos cheguem a ela, não será inserida duas vezes.

A matriz binária permanece separada da matriz de rótulos. Zero significa
sem rótulo, e todos os uns visitados por uma expansão recebem o ID da
semente. Quando a varredura externa encontra essas posições novamente,
ela reconhece que já foram contadas.

A versão iterativa evita recursão profunda. Como cada célula é visitada
no máximo uma vez e possui até oito vizinhos, o tempo sequencial é O(N),
com N igual à quantidade de células.”

Mostre rapidamente a rotina comum em `src/flood_fill.c`, destacando os
limites da região, a marcação e a inserção na pilha. Não leia o arquivo
inteiro linha por linha.

## 3:00–5:00 — Paralelização e compartilhamento

“No paralelo, divido a matriz em faixas horizontais. Cada thread executa
o mesmo flood fill, limitado às linhas que recebeu. Para dez linhas e
três threads, os tamanhos são quatro, três e três. Uso o quociente da
divisão e distribuo as linhas restantes nas primeiras faixas.

O número de threads é configurável. Se forem solicitadas mais threads
que linhas, limito a quantidade efetiva ao número de linhas.

Cada trabalhadora recebe uma estrutura com os limites de sua faixa,
acesso à entrada e aos rótulos e espaço para seu resultado local. O ID
de cada componente é o índice linear da semente mais um. Como cada
semente é uma célula diferente, não preciso de um contador global de IDs.

A entrada é compartilhada apenas para leitura. As threads escrevem no
mesmo vetor de rótulos, mas em posições disjuntas. Cada uma tem sua pilha
e sua contagem. Por isso não preciso de mutex no flood fill.

Depois de criar as trabalhadoras, a principal aguarda todas com
pthread_join. Só então lê os resultados e começa a consolidação.”

Mostre os limites das faixas e o laço de criação/join em
`src/conta-objetos-paralelo.c`.

## 5:00–7:00 — Fronteiras e Union-Find

“Somar as contagens locais ainda não dá a resposta. Aqui cada thread
encontra um componente, mas globalmente existe apenas um.”

Mostre os dois desenhos:

```text
Vertical:          Diagonal:
1                  1 0
---------          ---------
1                  0 1
```

“Para cada fronteira, comparo a última linha da faixa superior com a
primeira da inferior. Para um 1 na coluna c, verifico abaixo c menos um,
c e c mais um, respeitando as bordas.

Isso cobre todas as conexões externas possíveis: um vizinho da
conectividade 8 varia no máximo uma linha e uma coluna. As conexões
internas já foram tratadas pelo flood fill.

Quando encontro um par de uns, uno seus rótulos no Union-Find. Parent
guarda os pais e find encontra a raiz representante. A compressão de
caminho e a união por rank mantêm as consultas eficientes.

Inicio o total com a soma local e desconto um somente quando a união
junta duas raízes diferentes. Se os rótulos já estavam ligados, não
desconto novamente. A transitividade resolve também objetos que
atravessam três ou mais faixas.

Toda essa consolidação ocorre na principal depois dos joins, então
parent e rank não sofrem atualizações concorrentes.”

Mostre a condição que decrementa o total apenas após uma união efetiva.

## 7:00–9:00 — Testes e desempenho

“A correção precisa ser conferida separadamente do desempenho. As cinco
matrizes oficiais têm resultados esperados 3, 4, 5, 6 e 7. Também são
importantes os casos com apenas zeros, apenas uns, diagonais, componentes
cruzando fronteiras, divisão com resto e excesso de threads.”

Mostre `results/resultados.md`: 1.305 execuções aprovadas, incluindo os
cinco exemplos, 12 casos dirigidos, 64 matrizes 2 x 3, 100 aleatórias e
entradas inválidas. Threads solicitadas: 1, 2, 3, 4, 8 e linhas+5.

“Para desempenho, a mesma matriz deve ser usada em várias execuções do
sequencial e do paralelo. O intervalo inclui alocações do processamento,
criação e espera das threads, flood fill, consolidação e liberações. A
leitura da entrada e a impressão ficam fora nas duas versões.

O speedup é o tempo sequencial dividido pelo paralelo. Valor maior que um
significa aceleração; menor que um significa desaceleração. A estatística
das repetições e a configuração da máquina aparecem nos resultados.”

Mostre a tabela: mediana sequencial 0,317326 s; 2 threads 0,275012 s;
4 threads 0,192030 s; 8 threads 0,207393 s. São cinco medições após um
aquecimento, para a mesma matriz 1024 x 1024. Com 4 threads, speedup 1,652.
Diga explicitamente: “Medi em Linux emulado QEMU/TCG com quatro CPUs
virtuais. Isso não representa escalabilidade nativa. Oito threads não
melhoraram a mediana, e houve variabilidade entre as amostras.”

“Não espero aceleração ilimitada. Criar threads e consolidar tem custo;
há inicializações e trabalho sequencial, além de limites de processador
e memória. Em matrizes pequenas, o custo adicional pode superar o ganho.”

## 9:00–10:00 — Conclusão

“A ideia central é separar o problema em duas fases: identificar
componentes independentemente em regiões exclusivas e depois reconstruir
as conexões que atravessam as regiões.

O sequencial conta os grupos diretamente. O paralelo usa faixas, IDs
únicos e joins, e o Union-Find corrige a separação artificial criada pelas
fronteiras. A divisão das áreas de escrita elimina a necessidade de mutex
durante a identificação local.

Os fontes usam a linguagem C89 e interfaces POSIX para threads e relógio.
Os testes verificam a contagem; as medições mostram o efeito real do
paralelismo no ambiente utilizado.”

Encerre com uma observação específica sustentada pela tabela real, se
houver resultados medidos. Reserve as explicações detalhadas de código,
tratamento de erro e complexidade para as perguntas do professor.
