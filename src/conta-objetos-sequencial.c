#include "flood_fill.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    Matriz matriz;
    size_t *rotulos;
    size_t objetos;
    double inicio, fim;
    int ok;

    if (argc != 2) {
        fprintf(stderr, "Uso: %s arquivo.txt\n", argv[0]);
        return EXIT_FAILURE;
    }
    if (!matriz_ler(argv[1], &matriz))
        return EXIT_FAILURE;
    if (!tempo_agora(&inicio)) {
        matriz_liberar(&matriz);
        return EXIT_FAILURE;
    }
    rotulos = (size_t *)calloc(matriz.total, sizeof(size_t));
    if (rotulos == NULL) {
        fprintf(stderr, "Erro: sem memoria para os rotulos.\n");
        matriz_liberar(&matriz);
        return EXIT_FAILURE;
    }
    ok = rotular_faixa(&matriz, rotulos, 0, matriz.linhas, &objetos);
    free(rotulos);
    if (!tempo_agora(&fim))
        ok = 0;
    matriz_liberar(&matriz);
    if (!ok) {
        fprintf(stderr, "Erro: contagem sequencial nao concluida.\n");
        return EXIT_FAILURE;
    }
    printf("Objetos: %lu\nTempo: %.9f s\n", (unsigned long)objetos, fim - inicio);
    return EXIT_SUCCESS;
}
