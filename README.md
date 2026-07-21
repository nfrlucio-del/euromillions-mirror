# EuroMillions data mirror

Espelho de dados dos resultados do EuroMilhoes, para servir de **fonte de reserva**
da app "Analisador de Chaves" (App Jogos).

## Porque existe

A app abre em `file://` e so consegue atualizar-se com fontes que enviem o cabecalho
CORS `access-control-allow-origin: *`. A fonte principal (pedromealha) tem CORS mas
falha muito com `429 Too Many Requests`. A fonte mais fiavel (nunofcguerreiro) tem os
dados frescos mas **nao** serve CORS ao browser.

Este repo resolve o no: uma **GitHub Action** corre no servidor (sem restricao de CORS),
vai buscar os dados frescos 1x/dia e grava-os em [`em.json`](./em.json). A app le esse
ficheiro via **jsDelivr**, que garante CORS.

## Como a app o consome

```
https://cdn.jsdelivr.net/gh/<USER>/<REPO>@main/em.json
```

Formato compacto (numeros e estrelas ja ordenados):

```json
[["2026-07-17", 12,21,23,34,40, 9,10, 0], ...]
//  date        n1 n2 n3 n4 n5  s1 s2  jw
```

`jw` (vencedores do 1o premio) vem sempre a 0 — esta fonte nao o fornece. A app so o usa
nas estatisticas de jackpot e a fonte principal preenche-o quando disponivel.

## Manutencao

- `build_data.py` — gera o `em.json` a partir da fonte.
- `.github/workflows/update.yml` — corre diariamente as 06:00 UTC (e a mao em Actions ->
  "Update EuroMillions data" -> "Run workflow"). So faz commit se os dados mudarem.

Fonte dos dados: https://nunofcguerreiro.com/api-euromillions-json
