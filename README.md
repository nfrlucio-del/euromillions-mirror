# EuroMillions data mirror

Espelho de dados dos resultados do **EuroMilhoes** e do **EuroDreams**, para a app
"Analisador de Chaves" (App Jogos).

## Porque existe

A app abre em `file://` e so consegue atualizar-se com fontes que enviem o cabecalho
CORS `access-control-allow-origin: *`.

- **EuroMilhoes:** a fonte principal (pedromealha) tem CORS mas falha muito com
  `429 Too Many Requests`. A fonte mais fiavel (nunofcguerreiro) tem os dados frescos mas
  **nao** serve CORS ao browser. Aqui o espelho e a **reserva**.
- **EuroDreams:** a unica fonte completa (beatlottery.co.uk) **nao** serve CORS. Aqui o
  espelho e a **unica** forma de a app se atualizar sozinha.

Este repo resolve o no: uma **GitHub Action** corre no servidor (sem restricao de CORS),
vai buscar os dados frescos 1x/dia e grava-os em [`em.json`](./em.json) e [`ed.json`](./ed.json).

## Como a app o consome

Tenta primeiro `raw.githubusercontent.com` (cache de 5 min) e depois jsDelivr (cache mais
longa). Ambos servem CORS `*`.

```
https://raw.githubusercontent.com/<USER>/<REPO>/main/em.json
https://cdn.jsdelivr.net/gh/<USER>/<REPO>@main/em.json
```

Formatos compactos (numeros ja ordenados):

```json
// em.json
[["2026-07-17", 12,21,23,34,40, 9,10, 0], ...]
//  date        n1 n2 n3 n4 n5  s1 s2  jw
// ed.json
[["2026-11-02", 5,7,22,23,29,36, 1, 0], ...]
//  date        n1 .. n6         Sonho jw
```

`jw` = vencedores do 1o premio. No `em.json` vem sempre a 0 (a fonte nao o fornece; a fonte
principal da app preenche-o). No `ed.json` vem da propria tabela do beatlottery.

## Manutencao

- `build_data.py` — gera `em.json` e `ed.json`. Cada jogo e independente: se uma fonte
  falhar, esse ficheiro fica como estava. O `ed.json` nunca e substituido por uma recolha
  com menos de 300 sorteios.
- `.github/workflows/update.yml` — corre diariamente as 06:00 UTC (e a mao em Actions ->
  "Update EuroMillions data" -> "Run workflow"). So faz commit se os dados mudarem.

Fontes: https://nunofcguerreiro.com/api-euromillions-json ·
https://www.beatlottery.co.uk/eurodreams/draw-history
