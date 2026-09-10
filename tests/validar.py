#!/usr/bin/env python3
"""Verifica os executaveis reais contra uma referencia independente em Python."""

import argparse
import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def referencia(matriz):
    """Une arestas do grafo de celulas; nao utiliza flood fill nem faixas."""
    linhas, colunas = len(matriz), len(matriz[0])
    pais = {r * colunas + c: r * colunas + c
            for r in range(linhas) for c in range(colunas) if matriz[r][c]}

    def raiz(x):
        while pais[x] != x:
            x = pais[x]
        return x

    # Cada aresta e visitada uma vez: esquerda e tres vizinhos acima.
    for r in range(linhas):
        for c in range(colunas):
            if not matriz[r][c]:
                continue
            for dr, dc in ((0, -1), (-1, -1), (-1, 0), (-1, 1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < linhas and 0 <= cc < colunas and matriz[rr][cc]:
                    a, b = raiz(r * colunas + c), raiz(rr * colunas + cc)
                    pais[max(a, b)] = min(a, b)
    return len({raiz(x) for x in pais})


def ler_matriz(caminho):
    numeros = list(map(int, caminho.read_text(encoding="ascii").split()))
    linhas, colunas = numeros[:2]
    assert len(numeros) == 2 + linhas * colunas, caminho
    assert all(x in (0, 1) for x in numeros[2:]), caminho
    return [numeros[2 + r * colunas:2 + (r + 1) * colunas] for r in range(linhas)]


def gravar_matriz(caminho, matriz):
    with caminho.open("w", encoding="ascii", newline="\n") as arquivo:
        arquivo.write("{} {}\n".format(len(matriz), len(matriz[0])))
        for linha in matriz:
            arquivo.write(" ".join(map(str, linha)) + "\n")


def executar(binario, caminho, threads=None, timeout=20.0):
    comando = [str(binario), str(caminho)]
    if threads is not None:
        comando.append(str(threads))
    resultado = subprocess.run(comando, text=True, capture_output=True, timeout=timeout)
    if resultado.returncode != 0:
        raise AssertionError("{} falhou (codigo {}): {}".format(
            comando, resultado.returncode, resultado.stderr.strip()))
    campos = {}
    for campo, padrao in (
        ("objetos", r"^Objetos:\s*(\d+)\s*$"),
        ("tempo_s", r"^Tempo:\s*([0-9.eE+-]+)\s+s\s*$"),
        ("threads", r"^Threads:\s*(\d+)\s*$"),
    ):
        valores = re.findall(padrao, resultado.stdout, re.MULTILINE)
        if campo == "threads" and threads is None:
            continue
        if len(valores) != 1:
            raise AssertionError("Saida invalida de {}: {!r}".format(comando, resultado.stdout))
        campos[campo] = float(valores[0]) if campo == "tempo_s" else int(valores[0])
    if not math.isfinite(campos["tempo_s"]) or campos["tempo_s"] < 0:
        raise AssertionError("Tempo invalido: {}".format(campos))
    return campos


def dirigidos():
    return [
        ("somente_zeros", [[0] * 7 for _ in range(7)], 0),
        ("somente_uns", [[1] * 7 for _ in range(7)], 1),
        ("unico_1", [[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1),
        ("conexao_apenas_diagonal", [[int(r == c) for c in range(8)] for r in range(8)], 1),
        ("uma_fronteira", [[0, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 0]], 1),
        ("varias_fronteiras", [[0, 1, 0] for _ in range(12)], 1),
        ("componentes_proximos", [[1, 0, 1], [0, 0, 0], [1, 0, 1]], 4),
        ("mais_threads_que_linhas", [[1, 0, 0, 0, 1], [0, 1, 0, 1, 0]], 2),
        ("linhas_nao_divisiveis", [[1, 0, 1], [1, 0, 1], [0, 1, 0],
                                    [1, 0, 0], [0, 0, 1], [0, 0, 1], [0, 1, 0]], 2),
        ("diagonal_esquerda_na_fronteira", [[0, 0], [0, 1], [1, 0], [0, 0]], 1),
        ("uma_linha", [[1, 1, 0, 1, 0, 1]], 3),
        ("uma_coluna", [[1], [0], [1], [1], [0], [1]], 3),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequencial-only", action="store_true")
    parser.add_argument("--bin-dir", type=Path, default=ROOT / "bin")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--seed", type=int, default=20260910)
    parser.add_argument("--random-cases", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    if args.random_cases < 0 or args.timeout <= 0:
        parser.error("random-cases deve ser >= 0 e timeout > 0")
    args.bin_dir = args.bin_dir.resolve()
    executaveis = {"sequencial": args.bin_dir / "conta-objetos-sequencial"}
    if not args.sequencial_only:
        executaveis["paralelo"] = args.bin_dir / "conta-objetos-paralelo"
    registros = []
    resumo = {"status": "FALHOU", "data_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "modo": "somente sequencial" if args.sequencial_only else "sequencial e paralelo",
              "seed": args.seed, "referencia": "Union-Find das adjacencias 8, sem flood fill",
              "binarios_sha256": {}, "registros": registros}
    erro = None
    try:
        for nome, binario in executaveis.items():
            resumo["binarios_sha256"][nome] = hashlib.sha256(binario.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="conta-objetos-testes-") as temp:
            caminho_temp = Path(temp) / "matriz.txt"

            def testar(nome, grupo, matriz, esperado=None, arquivo=None):
                correto = referencia(matriz)
                if esperado is not None and correto != esperado:
                    raise AssertionError("{}: referencia {}, esperado {}".format(nome, correto, esperado))
                arquivo = arquivo or caminho_temp
                if arquivo == caminho_temp:
                    gravar_matriz(arquivo, matriz)
                registros_caso = []
                configuracoes = [("sequencial", None)]
                if not args.sequencial_only:
                    configuracoes += [("paralelo", t) for t in sorted({1, 2, 3, 4, 8, len(matriz) + 5})]
                for modo, threads in configuracoes:
                    observado = executar(executaveis[modo], arquivo, threads, args.timeout)
                    if observado["objetos"] != correto:
                        raise AssertionError("{} / {} / T={}: esperado {}, observado {}".format(
                            nome, modo, threads, correto, observado["objetos"]))
                    if threads is not None and observado["threads"] != min(threads, len(matriz)):
                        raise AssertionError("{}: numero efetivo de threads incorreto".format(nome))
                    registro = dict(caso=nome, grupo=grupo, linhas=len(matriz), colunas=len(matriz[0]),
                                    modo=modo, solicitadas=threads, esperado=correto, **observado)
                    registros.append(registro)
                    registros_caso.append(registro)
                if grupo == "obrigatorios":
                    print("{}: esperado={}, sequencial={}{}".format(nome, correto,
                          registros_caso[0]["objetos"], "" if args.sequencial_only else
                          ", paralelo={} (todas as configuracoes)".format(correto)), flush=True)

            for i, esperado in enumerate((3, 4, 5, 6, 7), 1):
                arquivo = ROOT / "tests" / "exemplos" / "exemplo{}.txt".format(i)
                testar("exemplo{}".format(i), "obrigatorios", ler_matriz(arquivo), esperado, arquivo)
            for nome, matriz, esperado in dirigidos():
                testar(nome, "dirigidos", matriz, esperado)
            for i, valores in enumerate(itertools.product((0, 1), repeat=6)):
                testar("exaustivo2x3_{:02d}".format(i), "exaustivos", [list(valores[:3]), list(valores[3:])])
            rng = random.Random(args.seed)
            for i in range(args.random_cases):
                linhas, colunas = rng.randint(1, 25), rng.randint(1, 25)
                densidade = (0.1, 0.3, 0.5, 0.7, 0.9)[i % 5]
                matriz = [[int(rng.random() < densidade) for _ in range(colunas)] for _ in range(linhas)]
                testar("aleatorio_{:03d}".format(i), "aleatorios", matriz)

            invalidas = {
                "vazio": "", "zero_linhas": "0 3\n", "negativo": "-2 3\n",
                "zero_colunas": "2 0\n", "dimensao_texto": "dois 2\n",
                "dimensao_decimal": "2.5 2\n", "sem_colunas": "2\n",
                "produto_overflow": "18446744073709551615 18446744073709551615\n",
                "dimensao_overflow": "999999999999999999999999999999999999 1\n",
                "faltando_celula": "2 2\n1 0 1\n", "celula_extra": "1 1\n1 0\n",
                "valor_2": "1 1\n2\n", "valor_negativo": "1 1\n-1\n",
                "valor_texto": "1 1\nx\n", "valor_decimal": "1 1\n1.0\n",
                "texto_extra": "1 1\n1\nlixo\n",
            }

            def deve_falhar(nome, modo, argumentos):
                comando = [str(executaveis[modo])] + [str(x) for x in argumentos]
                resultado = subprocess.run(comando, text=True, capture_output=True, timeout=args.timeout)
                if resultado.returncode <= 0 or not resultado.stderr.strip():
                    raise AssertionError("Entrada invalida {} / {}: esperava erro tratado, codigo={}, stderr={!r}".format(
                        nome, modo, resultado.returncode, resultado.stderr))
                registros.append(dict(caso=nome, grupo="invalidos", modo=modo,
                                      codigo_saida=resultado.returncode, stderr=resultado.stderr.strip()))

            for nome, conteudo in invalidas.items():
                caminho_temp.write_text(conteudo, encoding="ascii")
                for modo in executaveis:
                    deve_falhar(nome, modo, [caminho_temp] + ([2] if modo == "paralelo" else []))
            gravar_matriz(caminho_temp, [[1, 0], [0, 1]])
            for modo in executaveis:
                deve_falhar("sem_argumentos", modo, [])
                deve_falhar("arquivo_inexistente", modo, [Path(temp) / "nao-existe.txt"] +
                            ([2] if modo == "paralelo" else []))
                deve_falhar("argumento_extra", modo, [caminho_temp] + ([2] if modo == "paralelo" else []) + ["extra"])
            if "paralelo" in executaveis:
                deve_falhar("faltam_threads", "paralelo", [caminho_temp])
                for t in ("0", "-1", "abc", "1.5", "99999999999999999999999999999999"):
                    deve_falhar("threads_" + t, "paralelo", [caminho_temp, t])
        resumo["status"] = "PASSOU"
    except (AssertionError, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        erro = str(exc)
        resumo["erro"] = erro
    args.output_dir.mkdir(parents=True, exist_ok=True)
    resumo["execucoes_concluidas"] = len(registros)
    (args.output_dir / "validacao.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = ["# Resultados de correcao", "", "Status: **{}**. Modo: {}.".format(resumo["status"], resumo["modo"]),
          "", "Execucao UTC: {}. Seed: {}.".format(resumo["data_utc"], args.seed), "",
          "| Exemplo | Dimensoes | Esperado | Sequencial | Paralelo |", "|---|---|---:|---:|---|"]
    for i, esperado in enumerate((3, 4, 5, 6, 7), 1):
        feitos = [r for r in registros if r["caso"] == "exemplo{}".format(i)]
        seq = next((str(r["objetos"]) for r in feitos if r["modo"] == "sequencial"), "nao concluido")
        par = [r for r in feitos if r["modo"] == "paralelo"]
        matriz = ler_matriz(ROOT / "tests" / "exemplos" / "exemplo{}.txt".format(i))
        md.append("| {} | {} x {} | {} | {} | {} |".format(i, len(matriz), len(matriz[0]), esperado, seq,
                  "; ".join("T{}: {}".format(r["solicitadas"], r["objetos"]) for r in par) or "nao executado"))
    md += ["", "- {} execucoes concluidas e registradas em `validacao.json`.".format(len(registros)),
           "- Referencia independente: Union-Find das adjacencias, sem flood fill ou particionamento.",
           "- Cobertura planejada: 5 exemplos do PDF, 12 casos dirigidos, todas as 64 matrizes 2 x 3,",
           "  {} matrizes aleatorias e entradas invalidas.".format(args.random_cases),
           "- Paralelo: T = 1, 2, 3, 4, 8 e linhas + 5; valores repetidos sao executados uma vez.",
           "- Um resultado PASSOU exige a conclusao de toda a cobertura indicada para o modo selecionado."]
    if erro:
        md += ["", "Falha: " + erro]
    (args.output_dir / "resultados.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("{}: {} execucoes; resultados em {}".format(resumo["status"], len(registros), args.output_dir))
    if erro:
        print(erro, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
