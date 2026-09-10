# Perguntas para treinar a apresentação

Tente responder sem olhar. Use a resposta curta para falar com objetividade;
consulte a completa quando precisar justificar. Nas perguntas sobre
desempenho e testes, mostre os relatórios de execução e seus números reais.

## 1. O que seu programa conta?

**Resposta curta:** Componentes de células 1 conectadas pelos oito vizinhos.

**Resposta completa:** A entrada é uma matriz binária. Zero é fundo e um
é parte de um objeto. Duas células 1 pertencem ao mesmo objeto se existe
um caminho de uns entre elas, usando movimentos horizontais, verticais ou
diagonais. Não conto a quantidade de uns; conto os grupos conectados.

## 2. Por que as diagonais fazem parte do mesmo objeto?

**Resposta curta:** Porque o enunciado exige conectividade 8.

**Resposta completa:** Cada célula pode se conectar às oito posições ao
seu redor. Logo, dois uns que só se tocam por um canto são vizinhos nesse
modelo. A diagonal `1 0 / 0 1` forma um componente. Ignorar diagonais mudaria
a definição do problema e poderia aumentar incorretamente a contagem.

## 3. Como o sequencial evita contar um objeto duas vezes?

**Resposta curta:** Só inicia componente em um 1 sem rótulo; o flood fill
rotula todo o grupo.

**Resposta completa:** A varredura externa passa por todas as posições.
Quando encontra uma semente não visitada, incrementa o total e percorre
todas as células alcançáveis a partir dela. Nas visitas seguintes da
varredura, os demais uns daquele objeto já têm rótulo, então não iniciam
novos componentes.

## 4. Por que escolheu flood fill iterativo?

**Resposta curta:** Para não depender da profundidade da pilha de chamadas.

**Resposta completa:** Um componente grande pode produzir um caminho muito
comprido. Com recursão, isso poderia exigir muitas chamadas aninhadas.
A versão iterativa guarda os índices em uma pilha dinâmica explícita.
Ela permite controlar crescimento, verificar falhas de alocação e liberar
memória, embora também possa ficar sem memória.

## 5. Por que marcar uma célula antes de colocá-la na pilha?

**Resposta curta:** Para que outra descoberta não a insira novamente.

**Resposta completa:** Dois vizinhos já visitados podem alcançar a mesma
célula. Se a marcação só ocorresse na retirada da pilha, ambos poderiam
empilhá-la enquanto ela aguardava processamento. Marcando na inserção,
somente a primeira descoberta a coloca na pilha; as demais reconhecem
que ela já foi alcançada.

## 6. Qual a diferença entre processo e thread?

**Resposta curta:** Processo reúne recursos de uma execução; thread é um
fluxo de execução dentro dele.

**Resposta completa:** Threads do mesmo processo compartilham seu espaço
de memória, mas têm execução e pilhas de chamadas próprias. Isso permite
que as trabalhadoras usem a mesma matriz sem copiá-la para processos
separados. O compartilhamento facilita comunicação, mas exige organizar
corretamente leituras e escritas.

## 7. Concorrência e paralelismo são sinônimos?

**Resposta curta:** Não. Concorrência é progresso no mesmo intervalo;
paralelismo é execução simultânea.

**Resposta completa:** Um núcleo pode alternar entre várias threads e
produzir execução concorrente. Com núcleos disponíveis, diferentes threads
podem executar simultaneamente. O programa cria oportunidades de paralelismo
na identificação local; a simultaneidade e o ganho obtido dependem dos
recursos e do escalonamento da máquina.

## 8. Onde está o paralelismo real do seu código?

**Resposta curta:** Nas threads que executam flood fill em faixas diferentes.

**Resposta completa:** Cada trabalhadora percorre suas linhas, identifica
sementes, expande componentes e calcula sua contagem local. A principal
não calcula antecipadamente essas respostas. As threads fazem identificação
efetiva de componentes e podem realizar esse trabalho ao mesmo tempo;
depois a principal aguarda e consolida.

## 9. Por que escolheu faixas de linhas em vez de blocos?

**Resposta curta:** Simplifica a divisão, a propriedade de escrita e as
fronteiras que precisam ser verificadas.

**Resposta completa:** Uma faixa contém linhas completas. Duas faixas
consecutivas só podem se conectar através de duas linhas adjacentes, então
a consolidação examina três direções para baixo. Blocos também poderiam
funcionar, mas exigiriam tratar mais lados e encontros de blocos. Faixas
são uma escolha simples, não uma prova de desempenho sempre superior.

## 10. Como divide dez linhas entre três threads?

**Resposta curta:** Em faixas de quatro, três e três linhas.

**Resposta completa:** Calculo q=10/3=3 e r=10%3=1. As primeiras r faixas
recebem q+1 linhas, e as outras recebem q. Os intervalos são `[0,4)`,
`[4,7)` e `[7,10)`. Os limites superiores são exclusivos, então não existe
linha repetida nem linha esquecida.

## 11. Como a estratégia trata oito threads?

**Resposta curta:** Aplica a mesma fórmula de divisão a oito faixas efetivas,
se houver pelo menos oito linhas.

**Resposta completa:** A quantidade não é fixada no código. Para T=8,
calculo L/8 e L%8 e distribuo o resto nas primeiras faixas. Depois verifico
as sete fronteiras. A lógica de flood fill e união é a mesma; o desempenho
com oito threads precisa ser medido e não é automaticamente melhor.

## 12. O que acontece quando há mais threads que linhas?

**Resposta curta:** A quantidade efetiva é limitada ao número de linhas.

**Resposta completa:** Cada faixa deve conter pelo menos uma linha útil.
Por isso uso `min(Tsolicitada,L)`. Criar mais threads produziria faixas
vazias e custos adicionais sem identificação útil. A execução informa a
quantidade efetiva, que é a relevante para interpretar o resultado.

## 13. Aceitar uma thread contradiz o requisito de paralelismo?

**Resposta curta:** Não como configuração adicional; a demonstração exigida
usa duas ou mais threads efetivas.

**Resposta completa:** Uma thread permite comparar o custo da arquitetura
paralela sem distribuição do trabalho. Ela não demonstra execução paralela.
Para atender à parte concorrente do trabalho, executamos configurações
com pelo menos duas trabalhadoras efetivas e mostramos que cada uma
identifica componentes em sua faixa.

## 14. Por que simplesmente somar as contagens das threads está errado?

**Resposta curta:** Um único objeto pode aparecer em várias faixas e ser
contado localmente mais de uma vez.

**Resposta completa:** Cada flood fill é limitado à sua região. Dois uns
vizinhos em lados opostos de uma fronteira recebem contagens locais
separadas. A soma inicial considera esses pedaços distintos. A consolidação
registra que eles são o mesmo objeto e reduz o total quando uma união
realmente junta dois grupos diferentes.

## 15. E se a conexão entre faixas ocorrer apenas pela diagonal?

**Resposta curta:** Ela é encontrada nas comparações com c-1 ou c+1.

**Resposta completa:** Para um 1 na coluna c da linha superior, verifico
a linha inferior nas colunas c-1, c e c+1, quando válidas. As colunas
laterais capturam as duas diagonais. Assim, `1 0 / 0 1` atravessando a
fronteira é unido, mesmo que não exista um par vertical de uns.

## 16. Por que basta conferir c-1, c e c+1?

**Resposta curta:** Um vizinho em conectividade 8 muda linha e coluna em
no máximo uma posição.

**Resposta completa:** Para atravessar uma fronteira horizontal, a aresta
precisa ligar a última linha de uma faixa à primeira da seguinte. A
diferença de coluna desse par só pode ser -1, 0 ou +1. Ligações internas
já foram visitadas. Portanto, essas comparações cobrem todas as arestas
que faltavam, sem precisar procurar mais longe.

## 17. O que acontece se um objeto atravessar três faixas?

**Resposta curta:** As uniões sucessivas ligam todos os seus rótulos pela
transitividade.

**Resposta completa:** Se A é unido a B na primeira fronteira e B a C na
segunda, os três ficam no mesmo conjunto Union-Find. Não é necessário
comparar diretamente a primeira faixa com a terceira. Um caminho que
atravessa várias faixas é reconstruído a partir das conexões entre faixas
adjacentes.

## 18. Dois componentes da mesma faixa podem ser unidos no final?

**Resposta curta:** Sim, se houver um caminho que passa por outra faixa.

**Resposta completa:** Dois grupos podem estar separados quando observamos
apenas a região local, mas ambos podem se conectar a um terceiro grupo
da faixa vizinha. As duas uniões os tornam equivalentes. Isso mostra por
que a consolidação precisa manter equivalências transitivas, em vez de
apenas subtrair um valor fixo por fronteira.

## 19. O que mudaria se fosse conectividade 4?

**Resposta curta:** O flood fill usaria quatro vizinhos e a fronteira só
precisaria comparar a mesma coluna.

**Resposta completa:** As diagonais deixariam de representar conexões.
Internamente, usaríamos cima, baixo, esquerda e direita. Entre faixas
horizontais, a única aresta permitida seria vertical, de superior[c] para
inferior[c]. Não basta mudar apenas a consolidação: a definição precisa
ser a mesma nas duas fases.

## 20. O que representa o rótulo de uma célula?

**Resposta curta:** O identificador do componente local que a visitou.

**Resposta completa:** A matriz de rótulos é separada da entrada binária.
Zero indica ausência de rótulo; as células 1 visitadas recebem o ID de
sua semente. Depois da consolidação, os números originais podem continuar
diferentes, pois a equivalência global está no Union-Find. O maior rótulo
não é o número de objetos.

## 21. Por que os IDs gerados pelas threads não colidem?

**Resposta curta:** Cada semente usa seu índice linear único mais 1.

**Resposta completa:** A fórmula `linha*C+coluna+1` associa um número
diferente a cada célula válida. Sementes diferentes têm índices diferentes,
e as faixas não compartilham células. Logo, não preciso de um contador
global de IDs. Valido dimensões e tamanhos de alocação para que overflow
não invalide esse argumento.

## 22. Por que usar Union-Find?

**Resposta curta:** Para manter equivalências transitivas entre componentes
locais com pouca complexidade de código.

**Resposta completa:** As fronteiras fornecem pares de rótulos conectados.
Union-Find permite uni-los e descobrir rapidamente se dois rótulos já
estão no mesmo grupo. Isso evita percorrer toda a matriz para trocar
rótulos após cada conexão e resolve naturalmente objetos que atravessam
múltiplas fronteiras.

## 23. O que fazem parent, find e union?

**Resposta curta:** Parent guarda ligações; find encontra o representante;
union junta grupos diferentes.

**Resposta completa:** Cada elemento aponta para um pai, e a raiz aponta
para si mesma. Find segue esses pais até a raiz. Union chama find para
os dois elementos; se as raízes forem diferentes, liga uma árvore à outra.
Se já forem iguais, não reduz a quantidade de grupos.

## 24. O que são compressão de caminho e união por rank?

**Resposta curta:** São técnicas para manter os caminhos até as raízes curtos.

**Resposta completa:** Find pode redirecionar elementos visitados para mais
perto da raiz, economizando trabalho nas consultas seguintes. Na união,
o rank orienta qual raiz será ligada à outra; ranks iguais exigem aumentar
o rank da raiz escolhida. Após compressão, rank não deve ser interpretado
como a altura atual exata da árvore.

## 25. Por que não subtrair um objeto para cada par de uns na fronteira?

**Resposta curta:** Muitos pares podem ligar grupos que já foram unidos.

**Resposta completa:** Uma fronteira larga pode ter várias conexões entre
os mesmos componentes. Se eu subtraísse em todas elas, o total ficaria
menor que o correto. Subtraio somente quando union encontra raízes
diferentes e efetivamente funde dois conjuntos. Rótulos numéricos
diferentes, sozinhos, não garantem grupos distintos.

## 26. Existe condição de corrida na matriz de rótulos?

**Resposta curta:** O desenho evita a corrida porque cada thread usa
somente as posições da própria faixa.

**Resposta completa:** O vetor é compartilhado, mas as regiões escritas
são disjuntas. A thread também restringe suas leituras de rótulos no flood
fill à região que controla. A principal só consulta os resultados depois
dos joins. Essa justificativa depende dos limites serem respeitados em
todas as visitas, inclusive diagonais.

## 27. O que aconteceria se duas threads escrevessem na mesma célula?

**Resposta curta:** Elas poderiam disputar a marcação e causar uma corrida
de dados.

**Resposta completa:** Ambas poderiam observar o rótulo zero, iniciar
descobertas diferentes e escrever IDs conflitantes. Além de prejudicar a
contagem, acessos concorrentes conflitantes sem sincronização não têm
comportamento seguro para assumir em C/Pthreads. A solução elimina essa
situação por propriedade exclusiva das faixas.

## 28. Por que não precisa de mutex no flood fill?

**Resposta curta:** Não há estado mutável que duas trabalhadoras precisem
alterar ao mesmo tempo.

**Resposta completa:** A entrada é somente leitura, a pilha é privada,
os rótulos são separados por faixa e a contagem é local. O resultado só
é agregado pela principal após os joins. Um contador global compartilhado
exigiria outra estratégia de sincronização, mas nosso desenho não o usa.

## 29. O que pthread_join garante?

**Resposta curta:** No sucesso, a thread esperada terminou e seus resultados
podem ser consumidos pela principal.

**Resposta completa:** Join aguarda uma thread específica. A ordem das
fases é: iniciar trabalhadoras, aguardar todas, ler contagens e consolidar.
Assim, a consolidação não compete com escritas locais ainda em andamento.
Um retorno de erro precisa ser tratado; não posso fingir que a thread
terminou e liberar memória que ela talvez continue usando.

## 30. Qual a diferença entre pthread_join e mutex?

**Resposta curta:** Join espera término; mutex protege acesso durante a
execução concorrente.

**Resposta completa:** Mutex permite que apenas uma thread execute uma
região crítica por vez. Join organiza uma dependência de término: a
principal aguarda uma trabalhadora concluir. O programa usa essa dependência
entre as fases locais e a consolidação, além de dividir as áreas de escrita,
para não precisar de mutex no flood fill.

## 31. O que é deadlock e por que o seu protocolo não forma um?

**Resposta curta:** Deadlock é espera circular; nossas trabalhadoras não
esperam umas pelas outras.

**Resposta completa:** Não há ciclo de aquisição de mutexes nem joins entre
trabalhadoras. A principal espera, e cada trabalhadora executa uma tarefa
finita em sua faixa. Isso evita a espera circular no protocolo. Um bug
de laço infinito seria outro problema e ainda precisaria ser investigado;
não afirmo que join sozinho torna qualquer programa livre de bloqueios.

## 32. Qual trecho permanece sequencial?

**Resposta curta:** A preparação, a coordenação, a consolidação e a saída;
a identificação das faixas é paralela.

**Resposta completa:** A principal prepara estruturas e argumentos,
cria as threads, aguarda os joins, soma resultados e processa Union-Find
nas fronteiras. Alocações e inicializações densas também podem representar
custo O(N) fora do flood fill paralelo. Por isso não descrevo o programa
inteiro como se levasse apenas O(N/T).

## 33. Qual é a complexidade de tempo e memória?

**Resposta curta:** Sequencial O(N); trabalho local total O(N); fronteiras
O((T-1)*C) verificações; memória O(N+T).

**Resposta completa:** Cada célula é visitada no máximo uma vez e tem até
oito vizinhos. Com equilíbrio, a fase local pode se aproximar de O(N/T)
em tempo decorrido. As operações Union-Find nas fronteiras têm custo
amortizado O(alpha(N)); inicializar estruturas densas acrescenta O(N).
A entrada e os vetores, mais as pilhas locais somadas, usam memória
proporcional a N, além dos dados das T threads.

## 34. Por que o paralelo pode ser mais lento?

**Resposta curta:** Os custos de organização podem superar o trabalho
economizado, principalmente em matrizes pequenas.

**Resposta completa:** Criar threads, escalonar, aguardar, alocar estruturas
e consolidar fronteiras custa tempo. Também pode haver desequilíbrio
entre faixas e disputa por memória/cache. Mais threads não equivalem
automaticamente a mais núcleos disponíveis. O benchmark deve revelar
quando esses custos compensam e quando produzem desaceleração.

## 35. Como calcula e interpreta o speedup?

**Resposta curta:** Divido o tempo sequencial pelo paralelo; acima de 1
indica aceleração, abaixo de 1 indica desaceleração.

**Resposta completa:** Uso a mesma matriz e o mesmo intervalo de medição
nas duas versões. Depois comparo a estatística definida para as repetições,
como a mediana. Se tempos hipotéticos fossem 2 s e 1 s, o speedup seria 2.
Na apresentação, substituo exemplos didáticos pelos valores efetivamente
registrados nos resultados.

## 36. Como sabe que sequencial e paralelo são equivalentes?

**Resposta curta:** Pelo argumento das arestas internas/externas e pelos
testes com resultados esperados e referência independente.

**Resposta completa:** O flood fill cobre as conexões internas de cada
faixa; a consolidação cobre todas as externas. As uniões mantêm a mesma
conectividade global. Além desse argumento, comparo contagens nas cinco
matrizes oficiais e em casos de borda, diagonais, fronteiras e matrizes
adicionais. Igualdade entre duas versões, sozinha, não exclui um erro
compartilhado; resultados esperados independentes ajudam a detectá-lo.

## 37. Qual parte do programa está dentro do cronômetro?

**Resposta curta:** O processamento completo, incluindo alocações e
liberações próprias; entrada e impressão ficam fora.

**Resposta completa:** O intervalo inclui flood fill e, na versão paralela,
criação das threads, joins e consolidação. Também inclui as estruturas
necessárias à solução. Isso compara custos completos e evita esconder
o overhead do paralelo. Leitura da matriz e impressão são excluídas
consistentemente nas duas versões.

## 38. Por que usar CLOCK_MONOTONIC?

**Resposta curta:** Para medir intervalos sem depender de ajustes no relógio
de calendário.

**Resposta completa:** `clock_gettime` consulta um relógio monotônico,
apropriado para medir tempo decorrido. Ele inclui espera e efeitos de
escalonamento; não mede apenas CPU consumida. Verifico se a chamada teve
sucesso e uso a diferença entre fim e início. Várias repetições ajudam
a reduzir o peso de interferências isoladas.

## 39. Usar POSIX viola a exigência de C89?

**Resposta curta:** Não: C89 define a linguagem, enquanto POSIX fornece
interfaces de sistema exigidas pela solução.

**Resposta completa:** Os fontes respeitam sintaxe C89, com declarações
no início dos blocos, comentários tradicionais e sem VLA. Pthreads e
o relógio são interfaces POSIX. A macro `_POSIX_C_SOURCE`, definida antes
dos cabeçalhos, solicita suas declarações. A plataforma ainda precisa
realmente implementar essas APIs.

## 40. Como trata erros e recursos das threads?

**Resposta curta:** Verifico retornos e só libero memória compartilhada
quando sei que as trabalhadoras terminaram.

**Resposta completa:** Entrada e alocações são verificadas. Create/join
retornam seu próprio código de erro. Se uma criação falhar, aguardo as
threads que já começaram. Se não for possível confirmar término por um
join, não sigo o caminho normal liberando dados potencialmente em uso.
A contagem só é apresentada como válida se todas as fases necessárias
terminarem corretamente.
