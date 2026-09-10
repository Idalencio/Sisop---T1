# Auditoria técnica — 10/09/2026

## Compilação e vínculo com os testes

`compilacao.log` registra recompilação forçada com GCC 15.2.0, C89,
Wall/Wextra/pedantic e Werror. Não houve erro nem warning. SHA-256 dos
binários recompilados coincide com os registrados nos testes e benchmark:

- Sequencial: `c778b97c95381193b77ea107aeff2fe12a1a624b3d9bc0ad2328510bc4b2b914`.
- Paralelo: `c1cca9210d84793400ae6efe17c14aada8f858be05038216597e11750daed173`.

## Memória

Valgrind 3.25.1, Memcheck, exemplo 5:

- Sequencial: 4 alocações/4 liberações; zero bytes vivos ao sair; zero erros.
- Paralelo com 4 threads: 11 alocações/11 liberações; zero bytes vivos; zero erros.

Logs integrais: `valgrind-sequencial.log` e `valgrind-paralelo.log`.
Isso é evidência dessas execuções, não prova universal sobre todas as entradas.

## Concorrência

Helgrind foi tentado e **não concluiu**: falhou com uma asserção interna
`hg_handle_client_request: Assertion 'found' failed` durante a interceptação
de pthread_join. O log integral foi mantido em `helgrind.log`. Não se atribui
uma causa definitiva e não se afirma que esse teste passou.

Como verificação adicional, Valgrind DRD concluiu o exemplo 5 com 4 threads,
contando 7 objetos e registrando zero erros não suprimidos. O log `drd.log`
declara 155 ocorrências suprimidas em 50 contextos; não foram criadas
supressões personalizadas pelo projeto. Isso limita a força da conclusão.

A revisão do código também verificou: matriz binária imutável, escrita de
rótulos disjunta entre faixas, pilhas privadas e leitura dos resultados
depois dos joins. Union-Find só é modificado pela principal.

## Limites dos testes

Não foram injetadas falhas artificiais em malloc, pthread_create,
pthread_join ou clock_gettime. Seus retornos e caminhos de erro foram
revisados estaticamente. Não houve execução em macOS. Linux foi executado
localmente sob emulação QEMU/TCG; os tempos não medem escalabilidade nativa.

Comandos de reprodução em Linux, na pasta do projeto:

```sh
make CFLAGS='-O2 -std=c89 -Wall -Wextra -pedantic -Werror -pthread'
make test
valgrind --leak-check=full --error-exitcode=1 ./bin/conta-objetos-sequencial tests/exemplos/exemplo5.txt
valgrind --leak-check=full --error-exitcode=1 ./bin/conta-objetos-paralelo tests/exemplos/exemplo5.txt 4
valgrind --tool=drd --error-exitcode=1 ./bin/conta-objetos-paralelo tests/exemplos/exemplo5.txt 4
```
