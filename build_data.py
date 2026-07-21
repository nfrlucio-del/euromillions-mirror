#!/usr/bin/env python3
"""Espelho de dados do EuroMilhoes.

Vai buscar o historico completo a uma fonte fiavel (nunofcguerreiro API, que NAO
serve CORS ao browser) e grava-o em `em.json` num formato compacto que a app le
via jsDelivr (que garante CORS). Corre no GitHub Actions (lado servidor -> sem
problema de CORS).

Formato de `em.json`:
    [[date, n1,n2,n3,n4,n5, s1,s2, jw], ...]
    - numeros e estrelas ja ordenados por ordem crescente
    - jw = numero de vencedores do 1o premio; esta fonte NAO o fornece -> 0 (desconhecido).
      A app so o usa nas estatisticas de jackpot; a fonte principal (pedromealha) preenche-o
      quando estiver disponivel.
"""
import json
import urllib.request

URL = "https://nunofcguerreiro.com/api-euromillions-json?result=all"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (em-mirror bot)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)

    rows = []
    for d in data["drawns"]:
        n = sorted(int(d["number_%d" % i]) for i in range(1, 6))
        s = sorted(int(d["star_%d" % i]) for i in range(1, 3))
        rows.append([d["date"], n[0], n[1], n[2], n[3], n[4], s[0], s[1], 0])
    rows.sort(key=lambda x: x[0])

    with open("em.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, separators=(",", ":"))
    print("em.json: %d sorteios, ultimo %s" % (len(rows), rows[-1][0]))


if __name__ == "__main__":
    main()
