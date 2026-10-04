#include "flood_fill.h"
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const Matriz *matriz;
    size_t *rotulos;
    size_t inicio;
    size_t fim;
    size_t objetos;
    int ok;
} Faixa;

static void *trabalhar(void *argumento)
{
    Faixa *faixa;

    faixa = (Faixa *)argumento;
    faixa->ok = rotular_faixa(faixa->matriz, faixa->rotulos,
                              faixa->inicio, faixa->fim, &faixa->objetos);
    return NULL;
}

static size_t encontrar(size_t *parent, size_t id)
{
    size_t raiz, proximo;

    raiz = id;
    while (parent[raiz] != raiz)
        raiz = parent[raiz];
    while (parent[id] != id) {
        proximo = parent[id];
        parent[id] = raiz;
        id = proximo;
    }
    return raiz;
}

/* Retorna 1 somente quando dois conjuntos distintos viram um. */
static int unir(size_t *parent, unsigned char *rank, size_t a, size_t b)
{
    size_t troca;

    a = encontrar(parent, a);
    b = encontrar(parent, b);
    if (a == b)
        return 0;
    if (rank[a] < rank[b]) {
        troca = a;
        a = b;
        b = troca;
    }
    parent[b] = a;
    if (rank[a] == rank[b])
        ++rank[a];
    return 1;
}

static int contar_paralelo(const Matriz *matriz, size_t quantidade,
                           size_t *objetos)
{
    pthread_t *threads;
    Faixa *faixas;
    size_t *rotulos, *parent;
    unsigned char *rank;
    size_t i, linha, criadas, base, resto, superior, inferior;
    size_t c, vizinha, primeira, ultima, a, b;
    int codigo, ok;

    if (quantidade > ((size_t)-1) / sizeof(pthread_t) ||
        quantidade > ((size_t)-1) / sizeof(Faixa)) {
        fprintf(stderr, "Erro: quantidade de threads grande demais.\n");
        return 0;
    }
    threads = (pthread_t *)malloc(quantidade * sizeof(pthread_t));
    faixas = (Faixa *)calloc(quantidade, sizeof(Faixa));
    rotulos = (size_t *)calloc(matriz->total, sizeof(size_t));
    parent = NULL;
    rank = NULL;
    ok = threads != NULL && faixas != NULL && rotulos != NULL;
    criadas = 0;
    linha = 0;
    /* Divide as linhas sem deixar buracos nem faixas vazias. */
    base = matriz->linhas / quantidade;
    resto = matriz->linhas % quantidade;
    for (i = 0; ok && i < quantidade; ++i) {
        faixas[i].matriz = matriz;
        faixas[i].rotulos = rotulos;
        faixas[i].inicio = linha;
        linha += base + (i < resto ? 1 : 0);
        faixas[i].fim = linha;
        codigo = pthread_create(&threads[i], NULL, trabalhar, &faixas[i]);
        if (codigo != 0) {
            fprintf(stderr, "pthread_create: %s\n", strerror(codigo));
            ok = 0;
        } else {
            ++criadas;
        }
    }
    *objetos = 0;
    /* Todos foram criados antes de esperar; as faixas trabalham juntas. */
    for (i = 0; i < criadas; ++i) {
        codigo = pthread_join(threads[i], NULL);
        if (codigo != 0) {
            /* Nao liberar buffers que uma thread ainda pode acessar. */
            fprintf(stderr, "pthread_join: %s\n", strerror(codigo));
            exit(EXIT_FAILURE);
        }
        if (!faixas[i].ok)
            ok = 0;
        *objetos += faixas[i].objetos;
    }
    if (ok) {
        parent = (size_t *)malloc((matriz->total + 1) * sizeof(size_t));
        rank = (unsigned char *)calloc(matriz->total + 1, sizeof(unsigned char));
        ok = parent != NULL && rank != NULL;
    }
    if (ok) {
        for (i = 0; i <= matriz->total; ++i)
            parent[i] = i;
        /* Os trabalhadores terminaram. So a principal une as fronteiras. */
        for (i = 1; i < quantidade; ++i) {
            inferior = faixas[i].inicio * matriz->colunas;
            superior = inferior - matriz->colunas;
            for (c = 0; c < matriz->colunas; ++c) {
                a = rotulos[superior + c];
                if (a == 0)
                    continue;
                primeira = c > 0 ? c - 1 : 0;
                ultima = c + 1 < matriz->colunas ? c + 1 : c;
                /* Inclui as duas diagonais, alem do vizinho abaixo. */
                for (vizinha = primeira; vizinha <= ultima; ++vizinha) {
                    b = rotulos[inferior + vizinha];
                    if (b != 0 && unir(parent, rank, a, b))
                        --*objetos;
                }
            }
        }
    }
    free(rank);
    free(parent);
    free(rotulos);
    free(faixas);
    free(threads);
    if (!ok)
        fprintf(stderr, "Erro: contagem paralela nao concluida.\n");
    return ok;
}

int main(int argc, char **argv)
{
    Matriz matriz;
    size_t quantidade, objetos;
    double inicio, fim;
    int ok;

    if (argc != 3 || !inteiro_positivo(argv[2], &quantidade)) {
        fprintf(stderr, "Uso: %s arquivo.txt numero_de_threads\n", argv[0]);
        return EXIT_FAILURE;
    }
    if (!matriz_ler(argv[1], &matriz))
        return EXIT_FAILURE;
    if (quantidade > matriz.linhas)
        quantidade = matriz.linhas;
    if (!tempo_agora(&inicio)) {
        matriz_liberar(&matriz);
        return EXIT_FAILURE;
    }
    ok = contar_paralelo(&matriz, quantidade, &objetos);
    if (!tempo_agora(&fim))
        ok = 0;
    matriz_liberar(&matriz);
    if (!ok)
        return EXIT_FAILURE;
    printf("Objetos: %lu\nTempo: %.9f s\nThreads: %lu\n",
           (unsigned long)objetos, fim - inicio, (unsigned long)quantidade);
    return EXIT_SUCCESS;
}

