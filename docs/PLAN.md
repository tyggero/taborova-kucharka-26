# Plán: Táborová kuchyně 2026 — recepty, jídelníček a tisk

> Provozní kontext a aktuální stav jsou v `CLAUDE.md`. Tento dokument je
> detailní plán a postup po milnících.

## Kontext

Vaříme na skautském táboře **Tábor 26** (2026-07-02 → 2026-07-18, ~16 dní)
pro cca 40 strávníků. Recepty jsou v Notion databázi **🥘 Recepty** (~46
položek), jídelníček v Notion **🍱 Jídelníček**.

Cíle: vytěžit recepty do ručně editovatelného formátu, doplnit odhad nutričních
hodnot a alergenů, navrhnout hezkou tisknutelnou A4 šablonu receptu, sestavit
vyvážený a praktický jídelníček a vše připravit k tisku.

## Technický návrh

Data v **YAML** (jeden soubor na recept) + generátor v **Pythonu (Jinja2)**,
který z YAML vyrobí tisknutelné **HTML** stránky A4. Tisk do PDF z prohlížeče.

Schéma YAML viz libovolný soubor v `data/recepty/`. Klíčová pole: `porce_original`,
`suroviny` (surovina/mnozstvi/jednotka/poznamka), `postup`, `nutrice_na_porci`,
`alergeny`, `vegetarian`, `zdroj_dat`, `overit`.

- Škálování: šablona přepočítá množství faktorem `10 / porce_original` (sloupec
  „na 10 osob") + prázdný sloupec „na ___ osob" k ruční dopsání.
- Alergeny → výrazný box nahoře na A4.

## Strategie vytěžování

- **Foto recepty:** stáhnout JPEG z Notion S3 (signed URL expirují ~1 h),
  archivovat do `assets/recepty/`, přepsat přes vision do YAML. **Vyžaduje
  povolený egress** na `prod-files-secure.s3.us-west-2.amazonaws.com`.
- **URL recepty:** vytěžit z textu Notion stránky (auto-scrape), případně živá
  URL. Nejistá místa → `overit: true`. Nic se „nevymýšlí".

## Milníky a stav

- **M1 — Skeleton + šablona receptu** ✅ HOTOVO. Repo, `generuj.py`, CSS,
  A4 šablona, 2 ukázkové recepty. *(Vzhled šablony ještě k doladění s uživatelem.)*
- **M2 — Vytěžení receptů** 🟡 ROZPRACOVÁNO. 8 URL/textových receptů hotovo;
  ~38 foto receptů čeká na session s egress (viz CLAUDE.md).
- **M3 — Nutrice + alergeny** 🟡 ČÁSTEČNĚ. U vytěžených odhad doplněn; chybí
  `data/alergeny.yaml` (čeká se na seznam alergenů + omezení od uživatele) a
  dořešení `overit: true` receptů.
- **M4 — Rozvrh** ⬜ TODO. `data/jidelnicek.yaml` (zrcadlo Notion Jídelníčku) +
  `templates/rozvrh.html.j2` + `styles/rozvrh.css`. Generátor už má kostru
  `render_rozvrh()`.
- **M5 — Vyváženost a praktičnost** ⬜ TODO. `kontrola.py`: opakování jídel,
  denní kcal/makra, kolize alergenů, výletové dny (přenosný studený oběd).
  Společná iterace nad jídelníčkem.
- **M6 — Finalizace k tisku** ⬜ TODO. Doladit, vygenerovat finální výstupy,
  commit + push.

## Ověření

1. `pip install -r requirements.txt && python3 generuj.py recepty` bez chyby.
2. Otevřít `vystup/recepty/<recept>.html` → zkontrolovat A4 layout, zalomení,
   sloupec „na 10 osob" + ruční sloupec, box ALERGENY.
3. Tisk do PDF (Ctrl+P, A4).
4. `python3 kontrola.py` (až vznikne) → přehled jídelníčku.
5. Křížová kontrola receptů proti předloze v Notionu.
