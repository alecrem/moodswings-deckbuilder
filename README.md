# Mood Swings Deck Builder

A web app that generates randomized 45-card decks for the card game Mood Swings, with a text list and image grid view. Includes a pipeline to generate localized card images in Spanish and Japanese (or any language you translate).

## Obtaining Card Images

The `card_images/` folder must contain the 133 `.webp` card images. To download them from the official Mood Swings card notes page, use a Greasemonkey/Tampermonkey userscript:

1. Install a userscript manager such as [Tampermonkey](https://www.tampermonkey.net/) or [Violentmonkey](https://violentmonkey.github.io/).

2. Install the userscript [`moodswings-downloader.user.js`](moodswings-downloader.user.js) by opening that file in your userscript manager.

3. Navigate to the [Mood Swings card notes page](https://magic.wizards.com/en/news/feature/mood-swings-card-notes), then trigger the download via the Tampermonkey menu → **Download All Cards**, or press `Cmd+Alt+.`. Progress is shown in the browser tab title.

4. Move the downloaded images into `card_images/`:

```bash
mv ~/Downloads/*.webp card_images/
```

Verify you have all 133:

```bash
ls card_images/*.webp | wc -l
```

## Generating Localized Card Images

### 1. Fill in translations

Copy the sample CSV for your language and fill in the translated card names and text:

```bash
cp translations/cards_es.sample.csv translations/cards_es.csv
# or
cp translations/cards_ja.sample.csv translations/cards_ja.csv
```

Each row has `name_en`, `name_es` / `name_ja`, `color`, `rarity`, `text_en`, and `text_es` / `text_ja`. Fill in the translated columns. The `text_*` field supports `<strong>`, `<em>`, and `<br />` tags.

The glossary at `translations/glossary.csv` has EN/ES/JA translations of all game terms as a reference.

For Spanish card titles, place `Beleren2016SmallCaps-Bold.ttf` in the `fonts/` folder (search for *Beleren 2016 Small Caps*). Japanese uses system fonts and needs no additional download.

### 2. Generate blank cards

Erases the name bar and text box from each card image:

```bash
python generate_blank_cards.py
```

Output goes to `card_images_blank/`.

### 3. Render translated cards

Renders translated names and text onto the blank cards:

```bash
python generate_translated_cards.py
```

Output goes to `translated-es/images/` and `translated-ja/images/`.

Once generated, open `translated-es/index.html` or `translated-ja/index.html` directly in a browser — no server needed.

## Random Deck Generator

A FastAPI app that generates randomized 45-card decks. Requires a local server.

### Setup

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
uvicorn app:app --reload
```

Then open [http://localhost:8000](http://localhost:8000).

### Generate a Deck (CLI)

```bash
python deck_generator.py
```

## Development

### Tests

```bash
python -m pytest -v
```

Tests covering card generation logic and CSV data integrity (the CSV tests are skipped if the translation files are not present).

### Format and lint

```bash
black .
ruff check .
```

## Card Distribution

**Total: 133 cards** — 48 commons, 40 uncommons, 30 rares, 15 mythic rares

**Deck: 45 cards** — 23 commons, 14 uncommons, 6 rares, 2 mythic rares

## Project Structure

```
moodswings-deckbuilder/
├── app.py                           # FastAPI web server
├── index.html                       # Web app frontend
├── card_urls.json                   # Card name → image URL map
├── deck_generator.py                # Deck generation logic
├── generate_blank_cards.py          # Erases name/text areas from card images
├── generate_translated_cards.py     # Renders translations onto blank cards
├── moodswings-downloader.user.js    # Userscript to download card images
├── requirements.txt
├── tests/                           # Test suite
├── translations/
│   ├── glossary.csv                 # EN/ES/JA game term glossary
│   ├── cards_es.sample.csv          # Spanish CSV template (no text)
│   └── cards_ja.sample.csv          # Japanese CSV template (no text)
├── card_images/                     # Original card images (gitignored)
├── card_images_blank/               # Blanked card images (gitignored)
├── translated-es/
│   ├── index.html                   # Spanish static site
│   └── images/                      # Spanish card images (gitignored)
└── translated-ja/
    ├── index.html                   # Japanese static site
    └── images/                      # Japanese card images (gitignored)
```

The `static/` folder is deployed automatically to GitHub Pages on every push to `main`.
