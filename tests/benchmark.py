#!/usr/bin/env python3
"""Mede os executaveis reais, salva todas as amostras e calcula medianas."""

import argparse
import csv
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import random
import shlex
import statistics
import subprocess
import sys
import time

from validar import ROOT, executar


def informacoes_maquina(cc, cflags, ambiente):
    info = {
        "sistema": platform.platform(), "arquitetura": platform.machine(),
        "processador": platform.processor(), "cpus_logicas": os.cpu_count(),
        "python": platform.python_version(), "ambiente_de_execucao_informado": ambiente,
        "compilador_comando": cc, "flags_de_compilacao_informadas": cflags,
        "nota_flags": "As flags sao informadas pelo comando; conferir o log real da compilacao.",
    }
    if hasattr(os, "sched_getaffinity"):
        info["cpus_permitidas_afinidade"] = sorted(os.sched_getaffinity(0))
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for linha in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if linha.startswith("model name"):
                info["modelo_cpu"] = linha.split(":", 1)[1].strip()
                break
    memoria = Path("/proc/meminfo")
    if memoria.exists():
        info["memoria_total"] = memoria.read_text(encoding="ascii").splitlines()[0]
    try:
        versao = subprocess.run(shlex.split(cc) + ["--version"], text=True,
                                capture_output=True, timeout=10)
        info["compilador_versao"] = versao.stdout.strip() or versao.stderr.strip()
        info["compilador_consulta_codigo"] = versao.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        info["compilador_consulta_erro"] = str(exc)
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=1024)
    parser.add_argument("--cols", type=int, default=1024)
    parser.add_argument("--density", type=float, default=0.45)
    parser.add_argument("--seed", type=int, default=20260910)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--threads", nargs="+", type=int, default=[2, 4, 8])
    parser.add_argument("--sequencial-only", action="store_true")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--bin-dir", type=Path, default=ROOT / "bin")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--cc", default=os.environ.get("CC", "cc"))
    parser.add_argument("--cflags", default=os.environ.get(
        "CFLAGS", "-O2 -std=c89 -Wall -Wextra -pedantic -pthread"))
    parser.add_argument("--execution-environment", default="Nao informado; pode ser nativo, VM ou emulacao.")
    args = parser.parse_args()
    if args.rows < 1 or args.cols < 1 or not 0 <= args.density <= 1:
        parser.error("rows e cols devem ser positivos; density deve estar entre 0 e 1")
    if args.repetitions < 2 or args.warmups < 1 or args.timeout <= 0:
        parser.error("repetitions >= 2, warmups >= 1 e timeout > 0")
    if any(t < 1 for t in args.threads):
        parser.error("threads deve conter somente inteiros positivos")
    args.bin_dir, args.output_dir = args.bin_dir.resolve(), args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    matriz = args.output_dir / "matriz-benchmark.txt"
    resumo = {
        "status": "FALHOU", "data_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "maquina": informacoes_maquina(args.cc, args.cflags, args.execution_environment),
        "matriz": {"arquivo": matriz.name, "linhas": args.rows, "colunas": args.cols,
                   "densidade_solicitada": args.density, "seed": args.seed},
        "metodo": {"repeticoes_medidas": args.repetitions, "aquecimentos_por_configuracao": args.warmups,
                   "estatistica": "mediana", "ordem": "normal nas rodadas pares, invertida nas impares",
                   "tempo_usado": "campo Tempo do programa: contagem e estruturas auxiliares; sem leitura ou impressao",
                   "wall_time": "inclui processo, leitura e impressao; registrado, mas nao usado no speedup",
                   "justificativa_mediana": "Reduz a influencia de uma execucao isoladamente lenta, sem escolher o melhor tempo."},
        "binarios_sha256": {}, "configuracoes": [],
    }
    amostras = []
    erro = None
    try:
        configuracoes = [("sequencial", None)]
        if not args.sequencial_only:
            configuracoes += [("paralelo", t) for t in sorted(set(args.threads))]
        binarios = {nome: args.bin_dir / ("conta-objetos-" + nome) for nome, _ in configuracoes}
        for nome, binario in binarios.items():
            resumo["binarios_sha256"][nome] = hashlib.sha256(binario.read_bytes()).hexdigest()
        rng, uns = random.Random(args.seed), 0
        with matriz.open("w", encoding="ascii", newline="\n") as arquivo:
            arquivo.write("{} {}\n".format(args.rows, args.cols))
            for _ in range(args.rows):
                linha = ["1" if rng.random() < args.density else "0" for _ in range(args.cols)]
                uns += linha.count("1")
                arquivo.write(" ".join(linha) + "\n")
        resumo["matriz"].update(uns=uns, densidade_observada=uns / (args.rows * args.cols),
                                 sha256=hashlib.sha256(matriz.read_bytes()).hexdigest())
        objetos_esperados = None
        for fase, repeticoes in (("aquecimento", args.warmups), ("medicao", args.repetitions)):
            for repeticao in range(repeticoes):
                ordem = configuracoes if repeticao % 2 == 0 else list(reversed(configuracoes))
                for indice, (modo, threads) in enumerate(ordem, 1):
                    inicio = time.perf_counter()
                    resultado = executar(binarios[modo], matriz, threads, args.timeout)
                    wall = time.perf_counter() - inicio
                    if objetos_esperados is None:
                        objetos_esperados = resultado["objetos"]
                    if resultado["objetos"] != objetos_esperados:
                        raise AssertionError("{} T{} contou {}, referencia sequencial contou {}".format(
                            modo, threads, resultado["objetos"], objetos_esperados))
                    if threads is not None and resultado["threads"] != min(threads, args.rows):
                        raise AssertionError("Quantidade efetiva de threads incorreta")
                    amostras.append(dict(fase=fase, repeticao=repeticao + 1, ordem=indice, modo=modo,
                                         threads_solicitadas=threads or 0,
                                         threads_efetivas=resultado.get("threads", 0),
                                         objetos=resultado["objetos"], tempo_s=resultado["tempo_s"], wall_s=wall))
                    print("{} {}/{} {} T{}: {:.9f} s; objetos={}".format(fase, repeticao + 1,
                          repeticoes, modo, threads or 0, resultado["tempo_s"], resultado["objetos"]), flush=True)
        resumo["objetos"] = objetos_esperados
        tempo_seq = statistics.median(r["tempo_s"] for r in amostras if r["fase"] == "medicao" and r["modo"] == "sequencial")
        for modo, threads in configuracoes:
            registros = [r for r in amostras if r["fase"] == "medicao" and r["modo"] == modo
                         and r["threads_solicitadas"] == (threads or 0)]
            tempos = [r["tempo_s"] for r in registros]
            mediana = statistics.median(tempos)
            if mediana <= 0:
                raise AssertionError("Tempo mediano nao positivo; aumentar a matriz e repetir todas as configuracoes")
            resumo["configuracoes"].append(dict(modo=modo, threads_solicitadas=threads or 0,
                threads_efetivas=registros[0]["threads_efetivas"], repeticoes=len(tempos),
                mediana_s=mediana, minimo_s=min(tempos), maximo_s=max(tempos), speedup=tempo_seq / mediana))
        resumo["status"] = "PASSOU"
    except (AssertionError, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        erro = str(exc)
        resumo["erro"] = erro
    resumo["amostras_concluidas"] = len(amostras)
    with (args.output_dir / "desempenho.csv").open("w", encoding="utf-8", newline="") as arquivo:
        csvfile = csv.DictWriter(arquivo, fieldnames=["fase", "repeticao", "ordem", "modo", "threads_solicitadas",
            "threads_efetivas", "objetos", "tempo_s", "wall_s"])
        csvfile.writeheader()
        csvfile.writerows(amostras)
    (args.output_dir / "desempenho.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# Desempenho medido", "", "Status: **{}**.".format(resumo["status"]), "",
          "Data UTC: {}.".format(resumo["data_utc"]), "",
          "Ambiente declarado: {}".format(args.execution_environment), "",
          "Sistema: {}. CPUs logicas: {}.".format(resumo["maquina"]["sistema"], os.cpu_count()), "",
          "Matriz: {} x {}; densidade solicitada {}; seed {}.".format(args.rows, args.cols, args.density, args.seed), "",
          "{} aquecimento(s) por configuracao, descartados da mediana; {} repeticoes medidas.".format(args.warmups, args.repetitions),
          "Ordens alternadas a cada rodada. Todas as contagens concluidas foram comparadas com o primeiro sequencial.", "",
          "A mediana reduz a influencia de amostras isoladamente lentas. As amostras completas, inclusive",
          "aquecimentos, estao em `desempenho.csv`; hardware, hashes e compilador em `desempenho.json`.", "",
          "| Configuracao | Threads efetivas | Mediana (s) | Minimo (s) | Maximo (s) | Speedup |",
          "|---|---:|---:|---:|---:|---:|"]
    for config in resumo["configuracoes"]:
        nome = "Sequencial" if config["modo"] == "sequencial" else "{} threads".format(config["threads_solicitadas"])
        md.append("| {} | {} | {:.9f} | {:.9f} | {:.9f} | {:.3f} |".format(nome,
            config["threads_efetivas"] or "1 fluxo", config["mediana_s"], config["minimo_s"], config["maximo_s"], config["speedup"]))
    md += ["", "Speedup = mediana sequencial / mediana paralela. Valores menores que 1 indicam desaceleracao.",
           "O tempo usado e o campo `Tempo` do programa, que exclui leitura do arquivo e impressao.",
           "O tempo total do processo tambem foi registrado, mas nao entra no calculo do speedup.", "",
           "Os resultados descrevem esta matriz e este ambiente. Criacao de threads, alocacao, escalonamento,",
           "consolidacao sequencial e disputa por cache/memoria podem superar o ganho do processamento local.",
           "Se a execucao ocorreu em QEMU/TCG ou outra emulacao, os tempos nao representam a escalabilidade",
           "nativa do computador. Emulacao e CPUs virtuais precisam ser declaradas ao apresentar o experimento.",
           "Use a mesma entrada e as mesmas flags ao comparar; nao selecione apenas a melhor amostra."]
    if erro:
        md += ["", "Execucao incompleta: " + erro]
    (args.output_dir / "desempenho.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("{}: {} amostras; resultados em {}".format(resumo["status"], len(amostras), args.output_dir))
    if erro:
        print(erro, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
