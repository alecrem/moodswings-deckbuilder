from generate_blank_cards import (
    card_color,
    NAME_COVER,
    NAME_COVER_EXCEPTIONS,
    ONE_DIE_CARDS,
    TWO_DICE_CARDS,
)


class TestCardColor:
    def test_normal_format(self):
        assert card_color("Scorn (White Mythic Rare).webp") == "White"

    def test_normal_blue(self):
        assert card_color("Ambivalence (Blue Common).webp") == "Blue"

    def test_reversed_format(self):
        assert card_color("Frustration (Common Red).webp") == "Red"

    def test_reversed_format_glee(self):
        assert card_color("Glee (Common Red).webp") == "Red"

    def test_black(self):
        assert card_color("Apathy (Black Common).webp") == "Black"

    def test_green(self):
        assert card_color("Laziness (Green Common).webp") == "Green"

    def test_full_path(self):
        assert card_color("card_images/Anger (Red Uncommon).webp") == "Red"


class TestNameCoverExceptions:
    def test_rationalization_has_wider_cover(self):
        default_x2 = NAME_COVER[2]
        exc = NAME_COVER_EXCEPTIONS["Rationalization"]
        assert exc[2] > default_x2

    def test_rationalization_same_y(self):
        exc = NAME_COVER_EXCEPTIONS["Rationalization"]
        assert exc[1] == NAME_COVER[1]
        assert exc[3] == NAME_COVER[3]


class TestDiceCardSets:
    def test_no_overlap(self):
        assert ONE_DIE_CARDS.isdisjoint(TWO_DICE_CARDS)

    def test_known_one_die_cards(self):
        for name in ["Glee", "Chivalry", "Patience", "Condescension", "Curiosity"]:
            assert name in ONE_DIE_CARDS

    def test_known_two_dice_cards(self):
        for name in ["Altruism", "Love", "Happiness", "Superiority", "Vulnerability"]:
            assert name in TWO_DICE_CARDS
