# E-SIM Primera — Mapa de Fronteiras

Mapa interativo das regiões do servidor **Primera** do [E-SIM](https://primera.e-sim.org) e das fronteiras entre elas.

**Site:** https://matheuspio10.github.io/esim-fronteiras/

## O que dá pra ver
- **Região** — dono atual e legítimo, recurso e todos os vizinhos.
- **País** — regiões atacáveis, regiões de fronteira (pontes), regiões-chave do território, ocupações.
- **Rota** — caminho com menos conquistas (ou menos saltos) de um país/região até um destino, com aliados.
- **Fronteiras** — todos os pares de países vizinhos com as regiões-ponte; exporta CSV.
- **Pontos críticos** — fronteiras e regiões que são o único caminho para parte do mapa.

## Atualizar os dados
Os donos mudam com as guerras. Para coletar de novo e publicar:

```
python atualizar.py --publicar
```

A coleta leva ~6 minutos (lê as ~1000 páginas de região, 6 por vez).

## Arquivos
- `index.html` — o site (dados embutidos, funciona offline)
- `dados/regions.json` — dados coletados; `dados/pos.json` — posições do mapa
- `scripts/` — coleta (`scrape.py`), layout do grafo (`layout.py`), geração do HTML (`build.py` + `template.html`)
