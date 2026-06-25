#!/usr/bin/env python3
"""Generátor tisknutelných HTML stránek z YAML dat táborové kuchyně.

Použití:
    python3 generuj.py recepty   # vyrenderuje A4 recepty do vystup/
    python3 generuj.py rozvrh    # vyrenderuje rozvrh jídel do vystup/
    python3 generuj.py omezeni   # vyrenderuje manuál stravovacích omezení
    python3 generuj.py all       # vše

Data jsou v data/recepty/*.yaml a data/jidelnicek.yaml (ručně editovatelné).
Suroviny se pro tisk přepočítávají na PORCE_TISK osob; navíc zůstává prázdný
sloupec na ruční dopsání množství pro konkrétní počet strávníků.
"""
import sys
import os
import re
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RECEPTY_DIR = DATA / "recepty"
TEMPLATES = ROOT / "templates"
STYLES = ROOT / "styles"
VYSTUP = ROOT / "vystup"

# Na kolik osob se recept přepočítá pro tisk (viz plán – dopočet na 10 osob,
# zbytek se dopisuje ručně podle skutečného počtu strávníků).
PORCE_TISK = 10

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def nacti_css(jmeno):
    cesta = STYLES / jmeno
    return cesta.read_text(encoding="utf-8") if cesta.exists() else ""


def hezke_cislo(x):
    """Zaokrouhlí množství 'kuchařsky' a vrátí jako string bez zbytečných nul."""
    if x is None:
        return ""
    if x >= 10:
        x = round(x)
    elif x >= 1:
        x = round(x, 1)
    else:
        x = round(x, 2)
    if x == int(x):
        return str(int(x))
    return ("%g" % x).replace(".", ",")


def skaluj_suroviny(recept, cilove_porce):
    """Vrátí seznam surovin s přepočítaným množstvím na cilove_porce."""
    orig = recept.get("porce_original") or cilove_porce
    faktor = cilove_porce / orig if orig else 1
    vystup = []
    for s in recept.get("suroviny", []) or []:
        mn = s.get("mnozstvi")
        mn_skal = hezke_cislo(mn * faktor) if isinstance(mn, (int, float)) else ""
        vystup.append({
            "surovina": s.get("surovina", ""),
            "mnozstvi": mn_skal,
            "jednotka": s.get("jednotka", "") or "",
            "poznamka": s.get("poznamka", "") or "",
            "sekce": s.get("sekce", "") or "",
        })
    return vystup


def nacti_recepty():
    recepty = []
    for cesta in sorted(RECEPTY_DIR.glob("*.yaml")):
        with cesta.open(encoding="utf-8") as f:
            r = yaml.safe_load(f) or {}
        r.setdefault("id", cesta.stem)
        recepty.append(r)
    return recepty


def render_recepty():
    recepty = nacti_recepty()
    if not recepty:
        print("⚠  Žádné recepty v", RECEPTY_DIR)
        return
    sablona = env.get_template("recept.html.j2")
    # Vzhled lze přepnout: RECEPT_THEME=recept-minimal python3 generuj.py recepty
    tema = os.environ.get("RECEPT_THEME", "recept")
    css = nacti_css(f"{tema}.css") or nacti_css("recept.css")
    out_dir = VYSTUP / "recepty"
    out_dir.mkdir(parents=True, exist_ok=True)

    pripravene = []
    for r in recepty:
        ctx = dict(r)
        ctx["suroviny_skal"] = skaluj_suroviny(r, PORCE_TISK)
        ctx["porce_tisk"] = PORCE_TISK
        pripravene.append(ctx)
        html = sablona.render(recepty=[ctx], css=css, jeden=True)
        (out_dir / f"{r['id']}.html").write_text(html, encoding="utf-8")

    # Souhrnný soubor pro pohodlný tisk všeho najednou
    html = sablona.render(recepty=pripravene, css=css, jeden=False)
    (VYSTUP / "recepty-vse.html").write_text(html, encoding="utf-8")
    print(f"✓ Vygenerováno {len(recepty)} receptů → {out_dir}/ a recepty-vse.html")


def render_rozvrh():
    cesta = DATA / "jidelnicek.yaml"
    if not cesta.exists():
        print("⚠  data/jidelnicek.yaml zatím neexistuje – rozvrh přeskočen.")
        return
    with cesta.open(encoding="utf-8") as f:
        jidelnicek = yaml.safe_load(f) or {}
    recepty = {r["id"]: r for r in nacti_recepty()}
    sablona = env.get_template("rozvrh.html.j2")
    css = nacti_css("rozvrh.css")
    html = sablona.render(jidelnicek=jidelnicek, recepty=recepty, css=css)
    VYSTUP.mkdir(parents=True, exist_ok=True)
    (VYSTUP / "rozvrh.html").write_text(html, encoding="utf-8")
    print(f"✓ Vygenerován rozvrh → {VYSTUP / 'rozvrh.html'}")


def render_omezeni():
    """Vygeneruje A4 manuál stravovacích omezení z data/alergeny.yaml.

    Watch-list (seznam alergenů ke sledování) se odvodí jako sjednocení polí
    `alergeny` přes všechny strávníky – ručně se neudržuje.
    """
    cesta = DATA / "alergeny.yaml"
    if not cesta.exists():
        print("⚠  data/alergeny.yaml zatím neexistuje – manuál omezení přeskočen.")
        return
    with cesta.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    stravnici = data.get("stravnici") or []
    ciselnik = {a["id"]: a for a in (data.get("ciselnik_alergenu") or [])}

    # Odvození watch-listu: alergen -> kdo je jím dotčen, s popiskem a ikonou.
    watch = {}
    for s in stravnici:
        for alg in s.get("alergeny") or []:
            if alg not in ciselnik:
                print(f"⚠  Neznámý alergen '{alg}' u '{s.get('kdo', '?')}' "
                      f"– není v ciselnik_alergenu (překlep?).")
            zaznam = watch.setdefault(alg, {
                "id": alg,
                "nazev": ciselnik.get(alg, {}).get("nazev", alg),
                "ikona": ciselnik.get(alg, {}).get("ikona", "⚠️"),
                "koho": [],
            })
            zaznam["koho"].append(s.get("kdo", "?"))
    # Seřadit dle počtu dotčených (sestupně), pak abecedně dle názvu.
    watchlist = sorted(watch.values(), key=lambda w: (-len(w["koho"]), w["nazev"]))

    sablona = env.get_template("omezeni.html.j2")
    css = nacti_css("omezeni.css")
    html = sablona.render(
        nadpis="Stravovací omezení — Tábor 26",
        datum=data.get("datum", ""),
        stravnici=stravnici,
        watchlist=watchlist,
        css=css,
    )
    VYSTUP.mkdir(parents=True, exist_ok=True)
    (VYSTUP / "omezeni.html").write_text(html, encoding="utf-8")
    print(f"✓ Vygenerován manuál omezení ({len(stravnici)} strávníků, "
          f"{len(watchlist)} alergenů ke sledování) → {VYSTUP / 'omezeni.html'}")


def main():
    prikaz = sys.argv[1] if len(sys.argv) > 1 else "all"
    if prikaz in ("recepty", "all"):
        render_recepty()
    if prikaz in ("rozvrh", "all"):
        render_rozvrh()
    if prikaz in ("omezeni", "all"):
        render_omezeni()


if __name__ == "__main__":
    main()
