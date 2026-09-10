# Auditoria do enunciado — T1 de Sistemas Operacionais

Conferência em 10/09/2026 com o PDF de nove páginas. Marcas indicam
artefatos e execuções locais, não publicação, envio ou domínio pelo aluno.

## Implementação (páginas 1–3)

- [x] C89/C90, Linux e APIs POSIX; sem OpenMP ou dependência Windows nos fontes.
- [x] Compilação GCC 15.2.0 com `-O2 -std=c89 -Wall -Wextra -pedantic -Werror -pthread`.
- [x] Contagem de objetos binários por conectividade 8.
- [x] Sequencial com flood fill iterativo; validado antes de criar o paralelo.
- [x] Pilha dinâmica, marca de visita/rótulos e validação da entrada.
- [x] Pthreads diretamente, com trabalho real em cada faixa.
- [x] Quantidade configurável; testes com pelo menos duas threads efetivas.
- [x] Faixas equilibradas por quociente/resto; excesso limitado às linhas.
- [x] IDs únicos pela posição da semente mais 1, com limites de tamanho verificados.
- [x] Escritas restritas às faixas, entrada somente leitura, pilhas privadas.
- [x] Joins antes de consumir resultados; não há mutex desnecessário no flood fill.
- [x] Consolidação Union-Find: parent, encontrar/find, unir/union, rank e compressão.
- [x] Fronteiras verificam c-1, c, c+1: vertical e ambas as diagonais.
- [x] Conexões transitivas e uniões repetidas não geram dupla contagem.
- [x] Demonstração de conexões entre trabalhadores; faixas não exigem cruzamento
  artificial de quatro blocos. Justificativa no README e explicação completa.

## Correção (páginas 4–6)

- [x] Cinco matrizes transcritas e visualmente conferidas com o PDF.
- [x] Exemplo 1, 5 x 5: sequencial e paralelo = 3.
- [x] Exemplo 2, 6 x 8: sequencial e paralelo = 4.
- [x] Exemplo 3, 8 x 8: sequencial e paralelo = 5.
- [x] Exemplo 4, 9 x 12: sequencial e paralelo = 6.
- [x] Exemplo 5, 12 x 12: sequencial e paralelo = 7.
- [x] Zeros, uns, isolados, diagonais, uma/várias fronteiras e grupos próximos.
- [x] Resto da divisão e excesso de threads; uma linha e uma coluna.
- [x] Referência independente por adjacências, 64 casos exaustivos 2 x 3,
  100 matrizes aleatórias determinísticas e entradas inválidas.
- [x] 200 execuções da fase sequencial; depois 1.305 da suíte completa,
  documentadas em `results/sequencial/` e `results/validacao.json`.

## Desempenho e robustez (página 7)

- [x] Matriz grande determinística 1024 x 1024, seed 20260910.
- [x] Sequencial, 2, 4 e 8 threads; mesma matriz e flags.
- [x] Um aquecimento e cinco medições por configuração; 24 amostras totais.
- [x] Mediana, speedup e tempos brutos em CSV, JSON e Markdown.
- [x] Relógio monotônico; leitura/impressão excluídas consistentemente.
- [x] Emulação QEMU/TCG explicitamente declarada; sem alegar desempenho nativo.
- [x] Discussão de overhead, parte sequencial, variabilidade e limites de generalização.
- [x] Retornos POSIX, entrada e alocações verificados; falhas não viram contagem válida.
- [x] Liberação dos recursos no fluxo normal e nos erros recuperáveis.
- [x] Falha de join encerra processo sem liberar buffers possivelmente em uso.
- [x] Valgrind Memcheck no exemplo 5: zero erros e zero bytes ao sair nas duas versões.
- [x] Verificação adicional DRD no exemplo 5 com 4 threads: zero erros não
  suprimidos. Helgrind falhou internamente; detalhes em `results/AUDITORIA_TECNICA.md`.
- [ ] Injeção sistemática de falhas de malloc/create/join: não executada;
  caminhos foram revisados estaticamente. Não é alegada cobertura dinâmica total.
- [ ] Execução em macOS ou desempenho em Linux nativo: não executados;
  execução real confirmada em Linux emulado.

## Entrega e apresentação (páginas 7–9)

- [x] Organização src, tests e results; Makefile e README. Slides apenas locais.
- [x] Comandos de compilação, execução, testes, limpeza e benchmark.
- [x] Autoria editável, referências e declaração da assistência utilizada.
- [x] Explicação do zero em 20 seções; resumo de revisão.
- [x] 40 perguntas, cada uma com resposta curta e completa.
- [x] Roteiro de até 10 minutos e slides preparados localmente.
- [ ] Slides no repositório: omitidos a pedido do aluno nesta publicação.
- [ ] Conferir matrícula e eventual segundo integrante antes de publicar.
- [x] Repositório público de destino: https://github.com/Idalencio/Sisop---T1
- [ ] Enviar somente URL do repositório no Moodle até 06/10/2026, 23h59.
- [ ] Ensaio e domínio do código pelo aluno (e pelo colega, caso seja dupla).

Os itens pendentes de slides, envio e apresentação exigem ação do aluno;
nenhuma atividade foi submetida ou alterada no Moodle.
