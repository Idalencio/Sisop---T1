# T1 - Contagem de objetos: requisitos e fontes

## Estado desta preparação

O pedido completo do aluno e as nove páginas do PDF foram lidos em
10/09/2026, antes da implementação. As páginas também foram renderizadas
e inspecionadas visualmente, incluindo todas as células das cinco matrizes.
A sessão autenticada do Moodle confirmou o prazo abaixo.

## Fontes

- Disciplina: Sistemas Operacionais, turma 330, professor Filipo Novo Mor.
- Enunciado: https://moodle.pucrs.br/mod/resource/view.php?id=3903921
- PDF: https://moodle.pucrs.br/pluginfile.php/6167623/mod_resource/content/2/Trabalho_Pratico_Processos_Threads_Contagem_Objetos.pdf
- Material de apoio: https://moodle.pucrs.br/mod/resource/view.php?id=3903920
- Entrega: https://moodle.pucrs.br/mod/assign/view.php?id=3903923
- Prazo confirmado na página da entrega: **06/10/2026, 23h59**.

O aluno forneceu o PDF local após a primeira tentativa de download.
Fonte local: `Trabalho_Pratico_Processos_Threads_Contagem_Objetos.pdf`.
Não houve envio nem alteração de atividades no Moodle.

## Requisitos conferidos com o PDF e complementos do pedido

1. ANSI C89/C90, Linux/macOS, uso direto de Pthreads, sem OpenMP.
2. Compilação com `-std=c89 -Wall -Wextra -pedantic -pthread`.
3. Contar componentes de células 1 com conectividade 8; células 0 são fundo.
4. Implementar e validar primeiro a versão sequencial com flood fill
   iterativo e matriz de rótulos.
5. Implementar a versão paralela com faixas de linhas equilibradas,
   quantidade configurável de threads e identificação local real.
6. Gerar rótulos globais únicos por índice linear da semente mais 1.
7. Manter cada thread escrevendo exclusivamente em sua própria faixa.
8. Após todos os joins, consolidar fronteiras com Union-Find, incluindo
   ligações nas colunas c-1, c e c+1 da linha seguinte.
9. Conferir erros de alocação, entrada, relógio e chamadas POSIX relevantes;
   liberar recursos e explicar sincronização, memória e portabilidade.
10. Reproduzir exatamente as cinco matrizes do PDF. Resultados indicados
    no pedido: 5x5=3, 6x8=4, 8x8=5, 9x12=6 e 12x12=7.
11. Testar fundo vazio, preenchimento total, célula isolada, diagonais,
    uma e várias fronteiras, componentes próximos, excesso de threads e
    divisão de linhas com resto.
12. Comparar automaticamente sequencial e paralelo, incluindo matrizes
    determinísticas adicionais e várias quantidades de threads.
13. Medir uma matriz grande com sequencial, 2 e 4 threads; incluir 8 se o
    ambiente permitir. Repetir medições, justificar a estatística e
    calcular speedup. Nunca preencher resultados com tempos estimados.
14. Usar relógio monotônico POSIX e documentar a macro de exposição da API.
15. Fornecer Makefile com `make`, `make test`, `make clean` e
    `make benchmark`, além de README e resultados reproduzíveis.
16. Criar EXPLICACAO_COMPLETA.md, PERGUNTAS_APRESENTACAO.md (pelo menos
    30 perguntas, cada uma com resposta curta e completa),
    ROTEIRO_APRESENTACAO.md (até 10 minutos) e RESUMO_REVISAO.md.
17. Auditar todos os requisitos do PDF em CHECKLIST_ENUNCIADO.md antes de
    considerar o trabalho pronto.
18. Depois da implementação testada, iniciar uma simulação de banca no
    chat, uma pergunta por vez, vinculada ao código efetivamente criado.

## Exigências adicionais confirmadas no PDF

- Individual ou dupla; em dupla, ambos apresentam e explicam todo o código.
- Pelo menos duas unidades com trabalho real na demonstração paralela.
- As divisões laranja dos exemplos são ilustrativas. Como usamos faixas,
  devemos demonstrar travessias equivalentes entre trabalhadores, sem
  implementar artificialmente uma decomposição por blocos.
- `slides/apresentacao.pdf` é obrigatório (página 7, item 50).
- Todos os arquivos de entrega ficam em um repositório público GitHub;
  apenas o endereço do repositório é enviado no Moodle (páginas 7 e 9).
- Identificar ferramentas, bibliotecas e referências no README.
- O domínio e a apresentação pelo aluno são parte da avaliação e não
  podem ser substituídos pela geração destes materiais.

## Critérios de avaliação (página 9)

| Critério | Pontos |
| --- | ---: |
| Correção das versões e conectividade 8 | 2,0 |
| Decomposição e paralelismo efetivo | 1,5 |
| Sincronização e ausência de corridas | 1,5 |
| Consolidação de fronteiras | 1,5 |
| Testes e desempenho | 1,0 |
| C89 e tratamento de erros | 1,0 |
| Repositório e documentação | 0,5 |
| Apresentação e domínio | 1,0 |

## Estado de execução

- Leitura integral e conferência visual concluídas.
- Implementações concluídas; compilação real Linux C89 com Werror.
- Sequencial: 200 execuções antes da implementação paralela.
- Suíte completa: 1.305 execuções aprovadas; benchmark repetido registrado.
- Valgrind Memcheck: exemplo 5 nas duas versões, zero erros/vazamentos.
- Resultados em `results/`; repositório de destino `Idalencio/Sisop---T1`.
- Slides omitidos da publicação a pedido do aluno; envio ao Moodle pendente.

## Ordem de execução após a leitura integral

1. Completar a conferência dos requisitos e dos exemplos.
2. Fechar a arquitetura e o formato de entrada conforme o PDF.
3. Implementar sequencial; compilar e validar os cinco exemplos.
4. Implementar Pthreads e a consolidação das fronteiras.
5. Executar testes de correção, erro e memória disponíveis.
6. Executar benchmarks repetidos e interpretar os tempos reais.
7. Finalizar documentação, material de estudo e checklist auditado.
