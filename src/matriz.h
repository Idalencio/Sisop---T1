#ifndef MATRIZ_H
#define MATRIZ_H

#include <stddef.h>

typedef struct {
    size_t linhas;
    size_t colunas;
    size_t total;
    unsigned char *celulas;
} Matriz;

int matriz_ler(const char *caminho, Matriz *matriz);
void matriz_liberar(Matriz *matriz);
int inteiro_positivo(const char *texto, size_t *valor);
int tempo_agora(double *segundos);

#endif
