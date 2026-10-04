# Roteiro para apresentar o trabalho

Tempo estimado: 8 a 9 minutos, com demonstração curta. Use como apoio, não precisa decorar palavra por palavra. Tente explicar cada ideia olhando para o slide e para o código.

## Antes de começar

Lembre destas quatro ideias:

- Um objeto é um grupo de células 1 conectadas.
- A regra é conectividade 8, então a diagonal também conecta.
- Cada thread cuida de uma faixa de linhas.
- No fim, o programa une os rótulos que se encontram entre faixas.

## Slide 1 — Contagem de objetos (0:00 a 0:40)

**Fala sugerida**

“Oi, vou apresentar meu trabalho de Sistemas Operacionais. O programa conta quantos objetos aparecem numa matriz de zeros e uns. Primeiro vou explicar a busca sequencial, que uso como referência. Depois mostro como dividi a matriz entre threads e como tratei os objetos que passam de uma faixa para outra.”

**Transição**

“Antes de falar do código, vale entender o que o trabalho considera um objeto.”

## Slide 2 — Conectividade 8 (0:40 a 1:30)

**Fala sugerida**

“O zero representa o fundo e o um representa uma célula ocupada. O trabalho usa conectividade 8. Então uma célula pode se conectar com as oito posições em volta: acima, abaixo, dos lados e nas diagonais. No exemplo do slide, os dois uns se conectam pela diagonal e por isso contam como um objeto.”

**Se perguntarem a diferença para conectividade 4**

“Na conectividade 4 eu olharia só para cima, baixo, esquerda e direita. Como o enunciado pede conectividade 8, as diagonais também precisam ser consideradas.”

## Slide 3 — Busca sequencial (1:30 a 2:40)

**Fala sugerida**

“A versão sequencial percorre a matriz célula por célula. Quando encontra um um que ainda não tem rótulo, começa um objeto novo. Essa posição é a semente da busca. A função flood fill usa uma pilha para visitar as células vizinhas e marcar o grupo inteiro. Cada célula recebe um rótulo quando entra na pilha, então ela não volta para a busca. Quando o grupo termina, o programa continua a varredura.”

**Termos em palavras simples**

- **Semente:** a primeira célula do grupo que a busca encontrou.
- **Rótulo:** um número que identifica a qual objeto uma célula pertence.
- **Flood fill:** a busca que se espalha pelas células vizinhas do mesmo objeto.

**Se perguntarem por que a busca é iterativa**

“Uso uma pilha explícita em vez de chamar a função recursivamente. A busca continua fazendo o mesmo trabalho, mas não acumula uma chamada da função para cada célula.”

## Slide 4 — Divisão por faixas (2:40 a 3:40)

**Fala sugerida**

“Para paralelizar, separo a matriz em faixas de linhas. Divido o número de linhas pelo número de threads. O quociente dá o tamanho básico de cada faixa e o resto distribui as linhas que sobraram entre as primeiras. Por exemplo, dez linhas e três threads ficam com quatro, três e três linhas.”

**Como ler a tabela**

“O intervalo [0, 4) quer dizer que a faixa começa na linha zero e vai até antes da linha quatro. Então ela contém as linhas zero, um, dois e três.”

**Ideia importante**

Cada linha pertence a uma faixa. Isso evita deixar linha sem processamento e permite que as threads escrevam em regiões diferentes.

## Slide 5 — Threads e sincronização (3:40 a 4:40)

**Fala sugerida**

“A thread principal chama pthread_create para iniciar os trabalhadores. Cada um recebe os limites da própria faixa e processa aquela parte. Depois, pthread_join faz a principal esperar todas terminarem. A matriz original só é lida. Durante o flood fill, cada thread escreve nos rótulos das suas próprias linhas.”

**Se perguntarem por que não tem mutex no flood fill**

“As threads não escrevem na mesma parte dos rótulos. A união das fronteiras acontece só depois dos joins, na thread principal. Por isso essa etapa não está sendo executada por várias threads ao mesmo tempo.”

Não diga que o programa nunca precisa de sincronização: pthread_join é justamente o ponto em que a principal espera as outras.

## Slide 6 — União nas fronteiras (4:40 a 6:00)

**Fala sugerida**

“Pode acontecer de um mesmo objeto atravessar duas faixas. Cada thread o encontra na sua parte e dá um rótulo local. Depois dos joins, comparo a última linha de uma faixa com a primeira linha da seguinte. Para cada coluna, olho a mesma coluna e as duas colunas vizinhas. Assim verifico a ligação vertical e as duas diagonais.”

“Quando vejo que dois rótulos pertencem ao mesmo objeto, uso Union-Find para juntar os grupos. A contagem diminui só quando a união encontra duas raízes diferentes. Se a mesma conexão aparecer de novo, não desconto novamente.”

**Se perguntarem o que é Union-Find**

“É uma estrutura que acompanha quais rótulos já foram unidos. A função de busca encontra a raiz do grupo, e a união coloca dois grupos na mesma família.”

**Por que a checagem olha três colunas**

Na fronteira entre duas faixas, as ligações possíveis são a coluna de baixo e as duas diagonais. As outras células não são vizinhas daquela posição.

## Slide 7 — Resultados dos testes (6:00 a 7:00)

**Fala sugerida**

“Nesta tabela estão as cinco matrizes obrigatórias. O resultado sequencial, o paralelo com quatro threads e o esperado são iguais: três, quatro, cinco, seis e sete objetos. Além dessas matrizes, a suíte no GitHub Actions passou por 1.319 verificações no Linux. Ela inclui casos dirigidos, matrizes pequenas, casos aleatórios e entradas inválidas.”

**Se perguntarem como uma versão confere a outra**

“Além da comparação entre sequencial e paralela, os testes usam uma referência independente com Union-Find e adjacências. Isso ajuda a não depender apenas da mesma lógica do flood fill.”

## Slide 8 — Desempenho em Linux (7:00 a 8:10)

**Fala sugerida**

“O benchmark usa a mesma matriz de 1024 por 1024 em todas as configurações. Primeiro faz um aquecimento e depois mede cinco vezes. A tabela usa a mediana, que é o valor central das cinco medidas. Nesse runner Linux do GitHub, quatro threads tiveram speedup de aproximadamente 2,14 vezes. Oito threads ficaram quase iguais, com aproximadamente 2,13 vezes.”

“Isso não quer dizer que oito threads sempre sejam piores ou que quatro sempre sejam melhores. A execução foi numa máquina virtual do GitHub com quatro CPUs lógicas, usando uma matriz específica. Em outro computador ou com outra entrada, o tempo pode mudar.”

**Como explicar speedup**

“É o tempo sequencial dividido pelo tempo paralelo. Um speedup de 2,14 quer dizer que, nessa medição, a versão sequencial levou cerca de 2,14 vezes o tempo da paralela com quatro threads.”

**Fechamento**

“A versão sequencial me deu uma referência para comparar. Na paralela, as threads processam faixas diferentes e depois a thread principal une os objetos das fronteiras. Os testes passaram no Linux, e o benchmark mostra o resultado para o ambiente medido.”

## Demonstração opcional

Em um terminal Linux, dentro da pasta do projeto:

    make test
    ./bin/conta-objetos-paralelo tests/exemplos/exemplo5.txt 4

O primeiro comando roda a suíte. O segundo conta os objetos do exemplo 5 usando quatro threads. O teste Linux já foi executado no GitHub Actions; o endereço está no README do repositório.

## Perguntas rápidas para revisar

**O que significa conectividade 8?**  
Que cada célula considera os oito vizinhos, incluindo as diagonais.

**Por que existe uma versão sequencial?**  
Ela serve como uma implementação de referência para conferir a versão paralela.

**Como evitam contar duas vezes um objeto que cruza uma faixa?**  
As threads contam os componentes locais. Depois dos joins, a thread principal une os rótulos correspondentes nas fronteiras.

**Por que oito threads não foram mais rápidas do que quatro?**  
Neste teste as medianas ficaram quase iguais. Há quatro CPUs lógicas no runner e também existe custo para criar e coordenar threads. Não dá para generalizar para todo computador.

**A busca usa recursão?**  
Não. Usa uma pilha explícita e percorre os vizinhos de forma iterativa.

## Como ensaiar

1. Explique cada slide com suas palavras, sem ler o texto inteiro.
2. Treine a diferença entre a busca local de cada thread e a união final das fronteiras.
3. Se esquecer um detalhe, volte à ideia principal do slide e explique o exemplo.
4. Faça uma passada cronometrada. A demonstração pode ser curta se estiver perto dos dez minutos.

