#!/usr/bin/env python3
"""
Mood Swings Deck Generator
Generates randomized 45-card decks with the correct rarity distribution.

Cards are loaded from the card_images/ directory for a single source of truth.
"""

import random
import os
import re
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Card:
    """Represents a single card in Mood Swings."""

    name: str
    color: str
    rarity: str

    def __str__(self) -> str:
        return f"{self.name} ({self.color} {self.rarity})"


def parse_card_filename(filename: str) -> tuple[str, str, str] | None:
    """
    Parse a card filename in format: CardName (Color Rarity).webp
    or CardName (Rarity Color).webp
    Handles multi-word rarities like "Mythic Rare".

    Returns: (name, color, rarity) or None if invalid format
    """
    # Remove .webp extension
    if not filename.endswith(".webp"):
        return None

    name_part = filename[:-5]  # Remove .webp

    # Match pattern: something (content in parens)
    match = re.match(r"(.+?)\s+\(([^)]+)\)$", name_part)
    if not match:
        return None

    name, card_info = match.groups()
    parts = card_info.split()

    # Rarities and colors
    rarities = {"Common", "Uncommon", "Rare", "Mythic"}
    colors = {"White", "Blue", "Black", "Red", "Green"}

    # Try to identify which parts are color and which are rarity
    color_parts = []
    rarity_parts = []

    for part in parts:
        if part in colors:
            color_parts.append(part)
        elif part in rarities:
            rarity_parts.append(part)

    if not color_parts or not rarity_parts:
        return None

    color = color_parts[0]  # Should be only one color
    rarity = " ".join(rarity_parts)  # Handle "Mythic Rare"

    return name, color, rarity


def load_cards_from_directory(card_images_path: str) -> Dict[str, List[Card]]:
    """
    Load all cards from the card_images directory.
    Returns cards organized by rarity.
    """
    cards_by_rarity: Dict[str, List[Card]] = {
        "Common": [],
        "Uncommon": [],
        "Rare": [],
        "Mythic Rare": [],
    }

    card_dir = Path(card_images_path)
    if not card_dir.exists():
        raise FileNotFoundError(f"Card images directory not found: {card_images_path}")

    for filename in sorted(card_dir.iterdir()):
        if filename.is_file() and filename.suffix == ".webp":
            result = parse_card_filename(filename.name)
            if result:
                name, color, rarity = result
                card = Card(name, color, rarity)
                cards_by_rarity[rarity].append(card)

    return cards_by_rarity


# Load all 133 cards organized by rarity from card_images directory
_card_images_path = os.path.join(os.path.dirname(__file__), "card_images")
CARDS_BY_RARITY: Dict[str, List[Card]] = load_cards_from_directory(_card_images_path)


def generate_deck() -> List[Card]:
    """
    Generates a randomized 45-card Mood Swings deck.

    Distribution:
    - 23 commons
    - 14 uncommons
    - 6 rares
    - 2 mythic rares

    Returns:
        List of 45 Card objects
    """
    deck = []

    # Select cards by rarity
    deck.extend(random.sample(CARDS_BY_RARITY["Common"], 23))
    deck.extend(random.sample(CARDS_BY_RARITY["Uncommon"], 14))
    deck.extend(random.sample(CARDS_BY_RARITY["Rare"], 6))
    deck.extend(random.sample(CARDS_BY_RARITY["Mythic Rare"], 2))

    # Sort deck by rarity (for display)
    rarity_order = {"Common": 0, "Uncommon": 1, "Rare": 2, "Mythic Rare": 3}
    deck.sort(key=lambda card: (rarity_order[card.rarity], card.color, card.name))

    return deck


def print_deck(deck: List[Card]) -> None:
    """Prints a deck in a formatted manner."""
    color_count = {"White": 0, "Blue": 0, "Black": 0, "Red": 0, "Green": 0}
    rarity_count = {"Common": 0, "Uncommon": 0, "Rare": 0, "Mythic Rare": 0}

    # Count cards by rarity first
    for card in deck:
        rarity_count[card.rarity] += 1
        color_count[card.color] += 1

    print("\n" + "=" * 60)
    print("MOOD SWINGS DECK".center(60))
    print("=" * 60 + "\n")

    current_rarity = None
    for card in deck:
        if card.rarity != current_rarity:
            current_rarity = card.rarity
            print(
                f"\n{card.rarity.upper()}S ({rarity_count.get(card.rarity, 0)} in deck):"
            )
            print("-" * 60)

        print(f"  {card.name:<30} {card.color}")

    print("\n" + "=" * 60)
    print("DECK STATISTICS".center(60))
    print("=" * 60)
    print(f"\nRarity Breakdown:")
    print(f"  Commons:      {rarity_count['Common']}")
    print(f"  Uncommons:    {rarity_count['Uncommon']}")
    print(f"  Rares:        {rarity_count['Rare']}")
    print(f"  Mythic Rares: {rarity_count['Mythic Rare']}")
    print(f"  Total:        {sum(rarity_count.values())}")

    print(f"\nColor Breakdown:")
    for color in sorted(color_count.keys()):
        print(f"  {color:<10} {color_count[color]}")
    print("\n" + "=" * 60 + "\n")


def main() -> None:
    """Main entry point."""
    deck = generate_deck()
    print_deck(deck)


if __name__ == "__main__":
    main()
