# CLAUDE.md — kontext projektu pro Claude

Projekt: **podklady pro kuchyni na skautském táboře Tábor 26**
(2. – 18. 7. 2026, ~40 strávníků). Vytěžit recepty z Notionu → ručně
editovatelné YAML → tisknutelné **A4** stránky (HTML → tisk do PDF z prohlížeče)
+ vyvážený jídelníček a rozvrh k tisku.

Komunikace s uživatelem probíhá **česky**.

## Stav (aktualizováno 2026-06-18)

**Hotovo:** skeleton repa, generátor `generuj.py`, A4 šablona receptu
(`templates/recept.html.j2` + `styles/recept.css`), 8 vytěžených receptů
z URL/textu.

**Vytěženo (8):** kremova-cesnecka, spaghetti-carbonara, testoviny-s-pestem-a-cottage,
rajska-omacka-s-hovezim-masem, marry-me-chicken-pasta, vegan-butter-chicken,
red-lentil-curry, pasta-e-ceci.
Z toho **`overit: true`** (chybí část množství surovin): `red-lentil-curry`,
`pasta-e-ceci`, `spaghetti-carbonara`.

**Zbývá (~38 receptů) = foto/relační** — postup i množství jsou jen ve fotce
kuchařky vložené v Notionu; v textu stránky nic použitelného není. Např.:
Koprovka, Jáhlová kaše, Řecký kuskusový salát, Kuřecí paella, Čočkový salát,
Valašská pohanka, Chilli con carne, Květákový krém, Hrášková polévka, různé
pomazánky a kaše, Šopský salát, BLT Sandwich, Dušená mrkev… (úplný seznam =
data source Recepty v Notionu).

## ⚠️ Blokující předpoklad pro foto recepty: síťový egress

Fotky jsou v Notion S3 (`prod-files-secure.s3.us-west-2.amazonaws.com`),
signed URL **expirují ~1 h**. Egress allowlist se zamyká při startu kontejneru.
**Postup v nové session:**
1. Ověř přístup: `curl -sI <čerstvá signed URL z notion-fetch>` nesmí vrátit
   „Host not in allowlist".
2. Pokud blokováno → uživatel musí mít host v egress allowlistu a **spustit
   novou session** (změna se na běžící kontejner nepropíše).
3. Když projde: u každého foto receptu načti přes `notion-fetch` **čerstvou**
   signed URL obrázku, `curl` do `assets/recepty/<id>.jpg`, přečti Read
   (vision), přepiš do YAML (suroviny + postup), doplň nutrici/alergeny.

## Zdrojová data v Notionu

- **Recepty** (database `359a86fa-0044-803e-9bef-d71f29809895`,
  data source `collection://359a86fa-0044-809e-a9b4-000bba5c9037`).
  Vlastnosti: `Name`, `Odkaz` (URL), `Zdroj` (kuchařka), `Štítky`
  (Snídaně/Svačina/Oběd/Večeře/polévka/SAN Akce), `množství porcí`,
  `Suroviny` (relace — **IGNORUJEME**, viz rozhodnutí).
  - **URL recepty** (`Odkaz` vyplněn): postup+suroviny bývají v textu stránky
    (z auto-scrape Notionu) — vytěžitelné. Spolehlivost kolísá → primárně živá
    URL (WebFetch může vracet 403/bot-block), Notion text jako záloha.
  - **Foto recepty**: tělo = vložená DB surovin + JPEG fotka (S3, expiruje).
- **Jídelníček** (database `359a86fa-0044-805a-9484-d8b47f9e86e7`,
  data source `collection://359a86fa-0044-80a6-9366-000b6782e417`).
  Vlastnosti: `Datum`, `Den` (title), relace `Snídaně`/`Svačina 1`/`Oběd`/
  `Svačina 2`/`Večeře` → Recepty, `Poznámky`.
- **Tábor 26** page `2eba86fa-0044-80c5-9713-eb7eecfc5d4e`, termín
  2026-07-02 → 2026-07-18.

Pozn.: `notion-fetch` u vložených DB vrací jen schéma + filtr pohledu, NE řádky;
sémantický `notion-search` nad data source vrací prázdno. Suroviny foto receptů
proto z relace nejde vyčíst → bereme z fotky.

## Rozhodnutí uživatele (závazná)

- **Tisk:** HTML + CSS, tisk do PDF z prohlížeče. Žádný PDF renderer v env
  není (chromium/weasyprint nedostupné, apt/pypi egress omezený).
- **Porce:** ulož `porce_original` + suroviny na tento počet. Šablona přepočítá
  na **10 osob** a nechá prázdný sloupec „na ___ osob" k ruční dopsání.
- **Suroviny DB v Notionu IGNORUJEME** (děláme to v tomto repu).
- **Nutrice:** odhad kcal + bílkoviny/sacharidy/tuky na porci.
- **Alergeny:** výrazný box na receptu. Diety k zohlednění v jídelníčku:
  vegetariáni, bezlepkové/bezlaktózové; alergeny: **semínka, kokos, ořechy** +
  jedna holčička se speciálním omezením.
- **Registr `data/alergeny.yaml` existuje** (strávníci + číselník alergenů);
  generuje A4 manuál `vystup/omezeni.html` (`python3 generuj.py omezeni`) s tabulkou
  strávníků a odvozeným watch-listem alergenů. **Čeká se na uživatele:** doplnit
  skutečné strávníky (zatím placeholder záznamy) vč. speciálního omezení té holčičky.

## Repo a build

```bash
pip install -r requirements.txt
python3 generuj.py recepty      # nebo: make all
```
Výstup `vystup/recepty/*.html` + `vystup/recepty-vse.html`. Otevřít v prohlížeči,
Ctrl+P → Uložit jako PDF (A4). Jeden recept = jedna stránka.

| Cesta | Obsah |
|-------|-------|
| `data/recepty/*.yaml` | recepty (ručně editovatelné) — schéma viz kterýkoliv soubor |
| `data/jidelnicek.yaml` | rozvrh jídel (zatím neexistuje — Milník 4) |
| `data/alergeny.yaml` | registr strávníků s omezeními + číselník alergenů → manuál `vystup/omezeni.html` |
| `assets/recepty/` | archiv foto z kuchařek |
| `templates/`, `styles/` | HTML šablony a CSS |
| `generuj.py` | generátor; `PORCE_TISK = 10` |
| `kontrola.py` | kontrola jídelníčku (Milník 5, zatím neexistuje) |

YAML pole navíc: `zdroj_dat` (`foto`/`url`/`notion-text`), `overit` (true =
vytěžení nejisté, projít ručně).

## Další kroky (pořadí)

1. **(nová session s egress)** Vytěžit foto recepty → YAML + `assets/`.
2. Doplnit nutrici/alergeny, dořešit `overit: true` recepty.
3. Doladit šablonu receptu s uživatelem (společná iterace).
4. `data/jidelnicek.yaml` + rozvrh `templates/rozvrh.html.j2` (Milník 4).
5. `kontrola.py` — vyváženost, opakování, kolize alergenů, výletové dny (Milník 5).
6. Finalizace k tisku.

Detailní plán: `docs/PLAN.md`.

## Git

Vývojová větev: `claude/admiring-hopper-loieqf`. Commit message končí:
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```
NEpushovat do jiné větve bez výslovného svolení. Neuvádět model ID v commitech.
