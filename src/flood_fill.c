#include "flood_fill.h"
#include <stdlib.h>

typedef struct {
    size_t *itens;
    size_t tamanho;
    size_t capacidade;
} Pilha;

static int empilhar(Pilha *pilha, size_t valor, size_t limite)
{
    size_t capacidade;
    size_t *novo;

    if (pilha->tamanho == pilha->capacidade) {
        if (pilha->capacidade == limite)
            return 0;
        if (pilha->capacidade == 0)
            capacidade = limite < 256 ? limite : 256;
        else if (pilha->capacidade > limite / 2)
            capacidade = limite;
        else
            capacidade = pilha->capacidade * 2;
        novo = (size_t *)realloc(pilha->itens, capacidade * sizeof(size_t));
        if (novo == NULL)
            return 0;
        pilha->itens = novo;
        pilha->capacidade = capacidade;
    }
    pilha->itens[pilha->tamanho++] = valor;
    return 1;
}

int rotular_faixa(const Matriz *matriz, size_t *rotulos,
                  size_t inicio, size_t fim, size_t *objetos)
{
    Pilha pilha;
    size_t semente, posicao, vizinho, id, limite;
    size_t linha, coluna, l, c, primeira, ultima, esquerda, direita;

    pilha.itens = NULL;
    pilha.tamanho = pilha.capacidade = 0;
    *objetos = 0;
    limite = (fim - inicio) * matriz->colunas;
    for (semente = inicio * matriz->colunas;
         semente < fim * matriz->colunas; ++semente) {
        if (matriz->celulas[semente] == 0 || rotulos[semente] != 0)
            continue;
        /* O indice global evita repetir IDs em faixas diferentes. */
        id = semente + 1;
        if (!empilhar(&pilha, semente, limite)) {
            free(pilha.itens);
            return 0;
        }
        rotulos[semente] = id;
        ++*objetos;
        while (pilha.tamanho != 0) {
            posicao = pilha.itens[--pilha.tamanho];
            linha = posicao / matriz->colunas;
            coluna = posicao % matriz->colunas;
            primeira = linha > inicio ? linha - 1 : inicio;
            ultima = linha + 1 < fim ? linha + 1 : fim - 1;
            esquerda = coluna > 0 ? coluna - 1 : 0;
            direita = coluna + 1 < matriz->colunas ? coluna + 1 : coluna;
            for (l = primeira; l <= ultima; ++l) {
                for (c = esquerda; c <= direita; ++c) {
                    vizinho = l * matriz->colunas + c;
                    if (matriz->celulas[vizinho] && rotulos[vizinho] == 0) {
                        if (!empilhar(&pilha, vizinho, limite)) {
                            free(pilha.itens);
                            return 0;
                        }
                        /* Marca ao inserir: nenhuma celula entra duas vezes. */
                        rotulos[vizinho] = id;
                    }
                }
            }
        }
    }
    free(pilha.itens);
    return 1;
}

