import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from deck_generator import Card, generate_deck
from test_deck_generator import make_sample_cards

client = TestClient(app)

KNOWN_CARD = Card("Altruism", "White", "Rare")
KNOWN_URL = "https://media.wizards.com/2026/msw/xABg1Js9Np/en_1bc40321f2.webp"


def _sample_deck():
    return generate_deck(make_sample_cards())


def _deck_with_known_card():
    base = _sample_deck()
    return [KNOWN_CARD] + [
        c for c in base if not (c.name == "Rare0" and c.color == "White")
    ][:44]


class TestDeckEndpoint(unittest.TestCase):
    def test_returns_200(self):
        with patch("app.generate_deck", return_value=_sample_deck()):
            res = client.get("/api/deck")
        self.assertEqual(res.status_code, 200)

    def test_returns_45_cards(self):
        with patch("app.generate_deck", return_value=_sample_deck()):
            res = client.get("/api/deck")
        self.assertEqual(len(res.json()), 45)

    def test_card_has_required_fields(self):
        with patch("app.generate_deck", return_value=_sample_deck()):
            res = client.get("/api/deck")
        card = res.json()[0]
        self.assertIn("name", card)
        self.assertIn("color", card)
        self.assertIn("rarity", card)
        self.assertIn("image_url", card)

    def test_image_url_populated_from_card_urls(self):
        with patch("app.generate_deck", return_value=_deck_with_known_card()):
            res = client.get("/api/deck")
        cards = {c["name"]: c for c in res.json()}
        self.assertEqual(cards["Altruism"]["image_url"], KNOWN_URL)

    def test_image_url_none_when_not_in_map(self):
        with patch("app.generate_deck", return_value=_sample_deck()):
            res = client.get("/api/deck")
        # Fixture cards (e.g. "Common0") have no entry in card_urls.json
        self.assertIsNone(res.json()[0]["image_url"])


class TestIndexEndpoint(unittest.TestCase):
    def test_returns_200(self):
        res = client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_returns_html(self):
        res = client.get("/")
        self.assertIn("text/html", res.headers["content-type"])
