CC = cc
CFLAGS = -O2 -std=c89 -Wall -Wextra -Werror -pedantic -pthread
LDLIBS = -pthread
PYTHON = python3
COMUM = src/matriz.c src/flood_fill.c
CABECALHOS = src/matriz.h src/flood_fill.h

.PHONY: all sequencial test test-sequencial benchmark clean

all: bin/conta-objetos-sequencial bin/conta-objetos-paralelo

sequencial: bin/conta-objetos-sequencial

bin:
	mkdir -p bin

bin/conta-objetos-sequencial: src/conta-objetos-sequencial.c $(COMUM) $(CABECALHOS) | bin
	$(CC) $(CFLAGS) src/conta-objetos-sequencial.c $(COMUM) -o $@ $(LDLIBS)

bin/conta-objetos-paralelo: src/conta-objetos-paralelo.c $(COMUM) $(CABECALHOS) | bin
	$(CC) $(CFLAGS) src/conta-objetos-paralelo.c $(COMUM) -o $@ $(LDLIBS)

test-sequencial: sequencial
	$(PYTHON) tests/validar.py --sequencial-only

test: all
	$(PYTHON) tests/validar.py

benchmark: all
	$(PYTHON) tests/benchmark.py

clean:
	rm -f bin/conta-objetos-sequencial bin/conta-objetos-paralelo

