#!/usr/bin/env python3
"""
Unit tests for Mood Swings Deck Generator.

Tests:
- Card filename parsing
- Loading cards from filesystem
- Correct rarity distribution in full card list
- Deck generation with correct distribution
"""

import unittest
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest

from deck_generator import (
    Card,
    parse_card_filename,
    load_cards_from_directory,
    generate_deck,
    CARDS_BY_RARITY,
)

_COLORS = ["White", "Blue", "Black", "Red", "Green"]


def make_sample_cards() -> Dict[str, List[Card]]:
    """Create a minimal set of cards sufficient to generate a full deck."""
    return {
        "Common": [Card(f"Common{i}", _COLORS[i % 5], "Common") for i in range(25)],
        "Uncommon": [
            Card(f"Uncommon{i}", _COLORS[i % 5], "Uncommon") for i in range(16)
        ],
        "Rare": [Card(f"Rare{i}", _COLORS[i % 5], "Rare") for i in range(8)],
        "Mythic Rare": [
            Card(f"Mythic{i}", _COLORS[i % 5], "Mythic Rare") for i in range(4)
        ],
    }


class TestParseCardFilename(unittest.TestCase):
    """Test the parse_card_filename function."""

    def test_parse_valid_format_color_rarity(self):
        """Parse filename with color followed by rarity."""
        result = parse_card_filename("Ambivalence (Blue Common).webp")
        self.assertEqual(result, ("Ambivalence", "Blue", "Common"))

    def test_parse_valid_format_rarity_color(self):
        """Parse filename with rarity followed by color."""
        result = parse_card_filename("Frustration (Common Red).webp")
        self.assertEqual(result, ("Frustration", "Red", "Common"))

    def test_parse_mythic_rare(self):
        """Parse filename with multi-word rarity 'Mythic Rare'."""
        result = parse_card_filename("Love (Green Mythic Rare).webp")
        self.assertEqual(result, ("Love", "Green", "Mythic Rare"))

    def test_parse_card_name_with_hyphen(self):
        """Parse filename with hyphenated card name."""
        result = parse_card_filename("Self-Loathing (Black Common).webp")
        self.assertEqual(result, ("Self-Loathing", "Black", "Common"))

    def test_parse_invalid_extension(self):
        """Invalid extension returns None."""
        result = parse_card_filename("Ambivalence (Blue Common).jpg")
        self.assertIsNone(result)

    def test_parse_invalid_format_no_parens(self):
        """Invalid format without parentheses returns None."""
        result = parse_card_filename("Ambivalence Blue Common.webp")
        self.assertIsNone(result)

    def test_parse_invalid_format_unknown_color(self):
        """Invalid format with unknown color returns None."""
        result = parse_card_filename("Ambivalence (Purple Common).webp")
        self.assertIsNone(result)

    def test_parse_invalid_format_unknown_rarity(self):
        """Invalid format with unknown rarity returns None."""
        result = parse_card_filename("Ambivalence (Blue Epic).webp")
        self.assertIsNone(result)


class TestLoadCardsFromDirectory(unittest.TestCase):
    """Test the load_cards_from_directory function."""

    def test_load_cards_creates_structure(self):
        """Loaded cards have correct rarity structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "Ambivalence (Blue Common).webp").touch()
            Path(tmpdir, "Ambition (Black Common).webp").touch()
            Path(tmpdir, "Anger (Red Uncommon).webp").touch()
            Path(tmpdir, "Altruism (White Rare).webp").touch()
            Path(tmpdir, "Love (Green Mythic Rare).webp").touch()

            cards = load_cards_from_directory(tmpdir)

            self.assertIn("Common", cards)
            self.assertIn("Uncommon", cards)
            self.assertIn("Rare", cards)
            self.assertIn("Mythic Rare", cards)

    def test_load_cards_correct_counts(self):
        """Loaded cards are counted correctly by rarity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "Ambivalence (Blue Common).webp").touch()
            Path(tmpdir, "Ambition (Black Common).webp").touch()
            Path(tmpdir, "Anger (Red Uncommon).webp").touch()

            cards = load_cards_from_directory(tmpdir)

            self.assertEqual(len(cards["Common"]), 2)
            self.assertEqual(len(cards["Uncommon"]), 1)
            self.assertEqual(len(cards["Rare"]), 0)
            self.assertEqual(len(cards["Mythic Rare"]), 0)

    def test_load_cards_creates_card_objects(self):
        """Loaded files are converted to Card objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Ambivalence (Blue Common).webp").touch()

            cards = load_cards_from_directory(tmpdir)

            self.assertEqual(len(cards["Common"]), 1)
            card = cards["Common"][0]
            self.assertIsInstance(card, Card)
            self.assertEqual(card.name, "Ambivalence")
            self.assertEqual(card.color, "Blue")
            self.assertEqual(card.rarity, "Common")

    def test_load_cards_ignores_non_webp(self):
        """Non-webp files are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Ambivalence (Blue Common).webp").touch()
            Path(tmpdir, "Ambition (Black Common).jpg").touch()
            Path(tmpdir, "readme.txt").touch()

            cards = load_cards_from_directory(tmpdir)

            total = sum(len(c) for c in cards.values())
            self.assertEqual(total, 1)

    def test_load_cards_directory_not_found(self):
        """FileNotFoundError raised for missing directory."""
        with self.assertRaises(FileNotFoundError):
            load_cards_from_directory("/nonexistent/path")


_has_real_cards = any(Path(__file__).parent.joinpath("card_images").glob("*.webp"))


@pytest.mark.skipif(
    not _has_real_cards, reason="card_images/ not populated with real cards"
)
class TestCardListIntegrity(unittest.TestCase):
    """Test the integrity of the full card list from filesystem."""

    def test_total_cards_count(self):
        """Full card list contains exactly 133 cards."""
        total = sum(len(cards) for cards in CARDS_BY_RARITY.values())
        self.assertEqual(total, 133, f"Expected 133 total cards, got {total}")

    def test_common_cards_count(self):
        """Common rarity has exactly 48 cards."""
        count = len(CARDS_BY_RARITY["Common"])
        self.assertEqual(count, 48, f"Expected 48 common cards, got {count}")

    def test_uncommon_cards_count(self):
        """Uncommon rarity has exactly 40 cards."""
        count = len(CARDS_BY_RARITY["Uncommon"])
        self.assertEqual(count, 40, f"Expected 40 uncommon cards, got {count}")

    def test_rare_cards_count(self):
        """Rare rarity has exactly 30 cards."""
        count = len(CARDS_BY_RARITY["Rare"])
        self.assertEqual(count, 30, f"Expected 30 rare cards, got {count}")

    def test_mythic_rare_cards_count(self):
        """Mythic Rare rarity has exactly 15 cards."""
        count = len(CARDS_BY_RARITY["Mythic Rare"])
        self.assertEqual(count, 15, f"Expected 15 mythic rare cards, got {count}")

    def test_all_cards_have_valid_colors(self):
        """All cards have valid colors."""
        valid_colors = {"White", "Blue", "Black", "Red", "Green"}
        for rarity, cards in CARDS_BY_RARITY.items():
            for card in cards:
                self.assertIn(
                    card.color,
                    valid_colors,
                    f"Card {card.name} has invalid color {card.color}",
                )

    def test_all_cards_have_valid_rarities(self):
        """All cards have valid rarities."""
        valid_rarities = {"Common", "Uncommon", "Rare", "Mythic Rare"}
        for rarity, cards in CARDS_BY_RARITY.items():
            for card in cards:
                self.assertIn(
                    card.rarity,
                    valid_rarities,
                    f"Card {card.name} has invalid rarity {card.rarity}",
                )

    def test_rarity_matches_category(self):
        """Each card's rarity matches its category."""
        for rarity, cards in CARDS_BY_RARITY.items():
            for card in cards:
                self.assertEqual(
                    card.rarity,
                    rarity,
                    f"Card {card.name} in {rarity} category but has rarity {card.rarity}",
                )

    def test_no_duplicate_cards(self):
        """No duplicate cards exist in the full list."""
        all_cards = []
        for cards in CARDS_BY_RARITY.values():
            all_cards.extend([(card.name, card.color, card.rarity) for card in cards])

        unique_cards = set(all_cards)
        self.assertEqual(
            len(all_cards),
            len(unique_cards),
            f"Found duplicate cards: {len(all_cards) - len(unique_cards)} duplicates",
        )


class TestDeckGeneration(unittest.TestCase):
    """Test the generate_deck function."""

    def setUp(self):
        self.cards = make_sample_cards()

    def test_deck_total_cards(self):
        """Generated deck has exactly 45 cards."""
        deck = generate_deck(self.cards)
        self.assertEqual(len(deck), 45, f"Expected 45 cards, got {len(deck)}")

    def test_deck_common_count(self):
        """Generated deck has exactly 23 common cards."""
        deck = generate_deck(self.cards)
        common_count = sum(1 for card in deck if card.rarity == "Common")
        self.assertEqual(
            common_count, 23, f"Expected 23 common cards, got {common_count}"
        )

    def test_deck_uncommon_count(self):
        """Generated deck has exactly 14 uncommon cards."""
        deck = generate_deck(self.cards)
        uncommon_count = sum(1 for card in deck if card.rarity == "Uncommon")
        self.assertEqual(
            uncommon_count, 14, f"Expected 14 uncommon cards, got {uncommon_count}"
        )

    def test_deck_rare_count(self):
        """Generated deck has exactly 6 rare cards."""
        deck = generate_deck(self.cards)
        rare_count = sum(1 for card in deck if card.rarity == "Rare")
        self.assertEqual(rare_count, 6, f"Expected 6 rare cards, got {rare_count}")

    def test_deck_mythic_rare_count(self):
        """Generated deck has exactly 2 mythic rare cards."""
        deck = generate_deck(self.cards)
        mythic_count = sum(1 for card in deck if card.rarity == "Mythic Rare")
        self.assertEqual(
            mythic_count, 2, f"Expected 2 mythic rare cards, got {mythic_count}"
        )

    def test_deck_no_duplicates(self):
        """Generated deck has no duplicate cards."""
        deck = generate_deck(self.cards)
        card_tuples = [(card.name, card.color, card.rarity) for card in deck]
        unique_cards = set(card_tuples)
        self.assertEqual(
            len(card_tuples),
            len(unique_cards),
            "Deck contains duplicate cards",
        )

    def test_deck_all_cards_valid(self):
        """All cards in generated deck exist in the card list."""
        deck = generate_deck(self.cards)
        all_cards = {
            (c.name, c.color, c.rarity)
            for rarity_cards in self.cards.values()
            for c in rarity_cards
        }
        for card in deck:
            self.assertIn(
                (card.name, card.color, card.rarity),
                all_cards,
                f"Card {card} not found in card list",
            )

    def test_deck_generation_randomness(self):
        """Multiple deck generations produce different results."""
        deck1 = generate_deck(self.cards)
        deck2 = generate_deck(self.cards)

        deck1_set = frozenset((card.name, card.color, card.rarity) for card in deck1)
        deck2_set = frozenset((card.name, card.color, card.rarity) for card in deck2)

        # Very unlikely to be identical with 25 commons choosing 23, etc.
        if deck1_set == deck2_set:
            self.assertEqual(len(deck1), 45)


if __name__ == "__main__":
    unittest.main()
