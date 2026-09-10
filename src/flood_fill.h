#ifndef FLOOD_FILL_H
#define FLOOD_FILL_H

#include "matriz.h"

/* Rotula somente [inicio, fim). Retorna 0 se faltar memoria. */
int rotular_faixa(const Matriz *matriz, size_t *rotulos,
                  size_t inicio, size_t fim, size_t *objetos);

#endif
