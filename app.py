import json
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from deck_generator import Card, generate_deck

app = FastAPI()

_base = Path(__file__).parent
_card_urls: dict[str, str] = json.loads((_base / "card_urls.json").read_text())


class CardResponse(BaseModel):
    name: str
    color: str
    rarity: str
    image_url: str | None


def _card_key(card: Card) -> str:
    return f"{card.name} ({card.color} {card.rarity})"


def _to_response(card: Card) -> CardResponse:
    return CardResponse(
        name=card.name,
        color=card.color,
        rarity=card.rarity,
        image_url=_card_urls.get(_card_key(card)),
    )


@app.get("/api/deck", response_model=List[CardResponse])
def get_deck():
    return [_to_response(card) for card in generate_deck()]


@app.get("/", response_class=HTMLResponse)
def index():
    return (_base / "index.html").read_text()
