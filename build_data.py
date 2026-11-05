#!/usr/bin/env python3
"""Espelho de dados do EuroMilhoes e do EuroDreams.

As fontes fiaveis NAO servem CORS ao browser, por isso a app (aberta em `file://`) nao as
consegue ler diretamente. Este script corre no GitHub Actions (lado servidor -> sem problema
de CORS) e grava dois ficheiros compactos que a app le via raw.githubusercontent.com / jsDelivr
(ambos com CORS `*`):

`em.json` -- EuroMilhoes, fonte nunofcguerreiro API:
    [[date, n1,n2,n3,n4,n5, s1,s2, jw], ...]
    - jw = vencedores do 1o premio; esta fonte NAO o fornece -> 0 (desconhecido).
      A fonte principal da app (pedromealha) preenche-o quando estiver disponivel.

`ed.json` -- EuroDreams, fonte beatlottery.co.uk (tabela HTML por ano, desde 2023):
    [[date, n1..n6, dream, jw], ...]
    - jw = vencedores do 1o premio (6 + Sonho), vem da propria tabela.

Numeros ja ordenados por ordem crescente. Cada jogo e independente: se uma fonte falhar,
o ficheiro desse jogo fica como estava e o outro e atualizado na mesma.
"""
import datetime
import json
import re
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (em-mirror bot)"}
EM_URL = "https://nunofcguerreiro.com/api-euromillions-json?result=all"
ED_URL = "https://www.beatlottery.co.uk/eurodreams/draw-history/year/%d"
ED_FIRST_YEAR = 2023


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8")


def write(name, rows):
    rows.sort(key=lambda x: x[0])
    with open(name, "w", encoding="utf-8") as f:
        json.dump(rows, f, separators=(",", ":"))
    print("%s: %d sorteios, ultimo %s" % (name, len(rows), rows[-1][0]))


def build_em():
    rows = []
    for d in json.loads(get(EM_URL))["drawns"]:
        n = sorted(int(d["number_%d" % i]) for i in range(1, 6))
        s = sorted(int(d["star_%d" % i]) for i in range(1, 3))
        rows.append([d["date"]] + n + s + [0])
    write("em.json", rows)


def parse_ed_year(html):
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        m = re.search(r">(\d\d)/(\d\d)/(\d{4})</td>", tr)
        if not m:
            continue
        balls = sorted(int(x) for x in re.findall(r'ball-eurodreams">(\d+)<', tr))
        dream = re.findall(r'ball-eurodreams-dream">(\d+)<', tr)
        tds = re.findall(r"<td[^>]*>([^<]*)</td>", tr)
        jw = next((tds[i + 1].strip() for i, t in enumerate(tds[:-1]) if "&euro;" in t), "")
        if len(balls) != 6 or len(dream) != 1 or not jw.isdigit():
            raise ValueError("linha EuroDreams inesperada: %s" % m.group(0))
        rows.append(["%s-%s-%s" % (m.group(3), m.group(2), m.group(1))] + balls + [int(dream[0]), int(jw)])
    return rows


def build_ed():
    rows = []
    for y in range(ED_FIRST_YEAR, datetime.date.today().year + 1):
        rows += parse_ed_year(get(ED_URL % y))
    if len(rows) < 300:  # protecao: nunca substituir o historico por uma recolha partida
        raise ValueError("so %d sorteios EuroDreams -- recolha incompleta, ed.json mantido" % len(rows))
    write("ed.json", rows)


def main():
    failed = []
    for name, fn in (("em", build_em), ("ed", build_ed)):
        try:
            fn()
        except Exception as e:  # um jogo a falhar nao impede o outro
            print("ERRO %s: %s" % (name, e), file=sys.stderr)
            failed.append(name)
    if len(failed) == 2:
        sys.exit(1)


if __name__ == "__main__":
    main()
