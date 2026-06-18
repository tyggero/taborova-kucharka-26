# Táborová kuchyně 2026 🍳

Plánování jídelníčku, recepty a tisknutelné podklady pro kuchyni na skautském
táboře **Tábor 26** (2. – 18. 7. 2026, ~40 strávníků).

Recepty se vytěžují z Notion databáze do ručně editovatelných YAML souborů,
z nichž se generují **tisknutelné A4 stránky** (HTML → tisk do PDF z prohlížeče).

## Jak to funguje

```
data/recepty/*.yaml   →  generuj.py  →  vystup/recepty/*.html  →  tisk (Ctrl+P)
data/jidelnicek.yaml  →  generuj.py  →  vystup/rozvrh.html
```

- **Suroviny** se pro tisk přepočítávají na **10 osob**; na stránce zůstává
  prázdný sloupec „na ___ osob“ pro ruční doplnění podle skutečného počtu
  strávníků na dané jídlo.
- **Alergeny** se zvýrazňují v oranžovém boxu nahoře na receptu.
- **Nutrice** (kcal + makra na porci) jsou odhad.

## Spuštění

```bash
pip install -r requirements.txt
make all            # vygeneruje recepty i rozvrh do vystup/
# nebo: python3 generuj.py recepty
```

Výsledné HTML otevři v prohlížeči a vytiskni přes Ctrl+P → *Uložit jako PDF*
(formát A4, okraje „výchozí“). Jeden recept = jedna stránka.

## Struktura

| Cesta | Obsah |
|-------|-------|
| `data/recepty/*.yaml` | jednotlivé recepty (ručně editovatelné) |
| `data/jidelnicek.yaml` | rozvrh jídel po dnech |
| `data/alergeny.yaml` | registr alergenů a strávníků se speciálními omezeními |
| `assets/recepty/` | archiv předloh (foto z kuchařek) |
| `templates/`, `styles/` | HTML šablony a CSS pro tisk |
| `generuj.py` | generátor HTML |
| `kontrola.py` | kontrola vyváženosti a alergenů jídelníčku |
| `vystup/` | vygenerované stránky |

## Formát receptu (YAML)

Viz `data/recepty/kremova-cesnecka.yaml`. Pole `zdroj_dat` říká, odkud data
pochází (`foto` / `url` / `notion-text`), pole `overit: true` označuje recepty,
kde je vytěžení nejisté a je potřeba je projít ručně.
