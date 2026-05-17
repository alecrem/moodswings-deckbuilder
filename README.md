# Mood Swings Deck Builder

A web app that generates randomized 45-card decks for the card game Mood Swings, with a text list and image grid view.

## Features

- Generates randomized decks with proper rarity distribution
- 23 commons, 14 uncommons, 6 rares, 2 mythic rares
- Text list view grouped by rarity and color
- Image grid view with card art hotlinked from Wizards
- All 133 cards from Mood Swings included

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

**macOS/Linux:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the Web App

Start the development server:

```bash
uvicorn app:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

### Generate a Deck (CLI)

Run the deck generator from the command line:

```bash
python deck_generator.py
```

### Run Tests

Execute the full test suite:

```bash
python -m pytest -v
```

### Format and Lint

Check formatting with black:

```bash
black --check .
```

Apply formatting:

```bash
black .
```

Run the linter:

```bash
ruff check .
```

Tests validate:

- Card filename parsing (including multi-word rarities like "Mythic Rare")
- Loading cards from the `card_images/` filesystem
- Total card count: 133 cards (48 common, 40 uncommon, 30 rare, 15 mythic rare)
- Deck generation: exactly 45 cards with correct distribution (23 common, 14 uncommon, 6 rare, 2 mythic rare)
- No duplicate cards in deck
- All generated cards exist in the card list

## Card Distribution

**Total Cards: 133**

- Commons: 48
- Uncommons: 40
- Rares: 30
- Mythic Rares: 15

**Deck Contents: 45 cards**

- Commons: 23
- Uncommons: 14
- Rares: 6
- Mythic Rares: 2

## Downloading Card Images

The `card_images/` folder must contain the 133 `.webp` card images. To download them from the official Mood Swings card notes page, use a Greasemonkey/Tampermonkey userscript:

### Steps

1. Install a userscript manager such as [Tampermonkey](https://www.tampermonkey.net/) or [Violentmonkey](https://violentmonkey.github.io/).

2. Install the userscript [`moodswings-downloader.user.js`](moodswings-downloader.user.js) by opening that file in your userscript manager.

3. Navigate to:
   [https://magic.wizards.com/en/news/feature/mood-swings-card-notes](https://magic.wizards.com/en/news/feature/mood-swings-card-notes)

   Then trigger the download via the Tampermonkey menu → **Download All Cards**, or press `Cmd+Alt+.`. Progress is shown in the browser tab title.

4. Once all images are downloaded, move them into the `card_images/` folder in this project:

```bash
mv ~/Downloads/*.webp card_images/
```

   Verify you have all 133 images:

```bash
ls card_images/*.webp | wc -l
```

## Project Structure

```
moodswings-deckbuilder/
├── app.py                           # FastAPI app (web server + API)
├── index.html                       # Single-page frontend
├── card_urls.json                   # Card name → image URL map
├── deck_generator.py                # Deck generation logic
├── test_deck_generator.py           # Unit tests
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── moodswings-downloader.user.js    # Userscript to download card images
└── card_images/                     # Card image files (133 .webp, gitignored)
```
