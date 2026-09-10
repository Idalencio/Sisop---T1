#define _POSIX_C_SOURCE 200809L
#include "matriz.h"
#include <ctype.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int inteiro_positivo(const char *texto, size_t *valor)
{
    size_t numero;
    unsigned int digito;
    const unsigned char *p;

    numero = 0;
    p = (const unsigned char *)texto;
    if (*p == '\0')
        return 0;
    while (*p != '\0') {
        if (*p < '0' || *p > '9')
            return 0;
        digito = (unsigned int)(*p - '0');
        if (numero > ((size_t)-1 - digito) / 10)
            return 0;
        numero = numero * 10 + digito;
        ++p;
    }
    *valor = numero;
    return numero != 0;
}

/* Le um token inteiro sem permitir sinal, letras ou overflow. */
static int ler_numero(FILE *arquivo, size_t *valor)
{
    int ch;
    size_t numero;
    unsigned int digito;

    do {
        ch = fgetc(arquivo);
    } while (ch != EOF && isspace((unsigned char)ch));
    if (ch == EOF)
        return ferror(arquivo) ? -1 : 0;
    numero = 0;
    do {
        if (ch < '0' || ch > '9')
            return -1;
        digito = (unsigned int)(ch - '0');
        if (numero > ((size_t)-1 - digito) / 10)
            return -1;
        numero = numero * 10 + digito;
        ch = fgetc(arquivo);
    } while (ch != EOF && !isspace((unsigned char)ch));
    if (ferror(arquivo))
        return -1;
    *valor = numero;
    return 1;
}

int matriz_ler(const char *caminho, Matriz *matriz)
{
    FILE *arquivo;
    size_t i;
    size_t valor;
    int ok;

    matriz->celulas = NULL;
    matriz->linhas = matriz->colunas = matriz->total = 0;
    arquivo = fopen(caminho, "r");
    if (arquivo == NULL) {
        perror(caminho);
        return 0;
    }
    ok = ler_numero(arquivo, &matriz->linhas) == 1;
    if (ok)
        ok = ler_numero(arquivo, &matriz->colunas) == 1;
    if (ok)
        ok = matriz->linhas != 0 && matriz->colunas != 0;
    if (ok)
        ok = matriz->linhas <= ((size_t)-1) / matriz->colunas;
    if (ok) {
        matriz->total = matriz->linhas * matriz->colunas;
        /* Reserva margem para N+1 rotulos e para imprimir com %lu. */
        ok = matriz->total < ((size_t)-1) / sizeof(size_t)
             && matriz->total <= ULONG_MAX;
    }
    if (ok) {
        matriz->celulas = (unsigned char *)malloc(matriz->total);
        ok = matriz->celulas != NULL;
    }
    for (i = 0; ok && i < matriz->total; ++i) {
        ok = ler_numero(arquivo, &valor) == 1 && valor <= 1;
        if (ok)
            matriz->celulas[i] = (unsigned char)valor;
    }
    if (ok)
        ok = ler_numero(arquivo, &valor) == 0;
    if (fclose(arquivo) != 0) {
        perror("fclose");
        ok = 0;
    }
    if (!ok) {
        fprintf(stderr, "Erro: matriz invalida, grande demais ou sem memoria.\n");
        matriz_liberar(matriz);
    }
    return ok;
}

void matriz_liberar(Matriz *matriz)
{
    free(matriz->celulas);
    matriz->celulas = NULL;
}

int tempo_agora(double *segundos)
{
    struct timespec instante;

    if (clock_gettime(CLOCK_MONOTONIC, &instante) != 0) {
        perror("clock_gettime");
        return 0;
    }
    *segundos = (double)instante.tv_sec + (double)instante.tv_nsec / 1e9;
    return 1;
}
