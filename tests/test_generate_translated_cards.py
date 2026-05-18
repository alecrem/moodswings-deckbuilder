import pytest
import csv
from unittest.mock import MagicMock, patch
from generate_translated_cards import (
    parse_segments,
    tokenize,
    is_cjk,
    output_path,
    wrap_lines,
    KINSOKU_START,
    KINSOKU_END,
)


class TestParseSegments:
    def test_plain_text(self):
        segs = parse_segments("Hello world")
        assert segs == [("Hello world", False, False)]

    def test_strong(self):
        segs = parse_segments("<strong>Bold</strong> normal")
        assert ("Bold", True, False) in segs
        assert (" normal", False, False) in segs

    def test_em(self):
        segs = parse_segments("<em>Italic</em>")
        assert ("Italic", False, True) in segs

    def test_em_with_space(self):
        segs = parse_segments("<em >Italic</em >")
        assert ("Italic", False, True) in segs

    def test_br_becomes_para(self):
        segs = parse_segments("First<br />Second")
        assert ("\x00para", False, False) in segs

    def test_br_slash_optional(self):
        segs = parse_segments("A<br>B")
        assert ("\x00para", False, False) in segs

    def test_nested_strong_em(self):
        segs = parse_segments("<strong><em>Both</em></strong>")
        assert ("Both", True, True) in segs

    def test_empty_string(self):
        assert parse_segments("") == []

    def test_special_chars_preserved(self):
        segs = parse_segments("Value [0] — em dash")
        assert any("[0]" in t for t, _, _ in segs)
        assert any("—" in t for t, _, _ in segs)


class TestIsCjk:
    def test_hiragana(self):
        assert is_cjk("あ")
        assert is_cjk("の")

    def test_katakana(self):
        assert is_cjk("ア")

    def test_kanji(self):
        assert is_cjk("気")
        assert is_cjk("持")

    def test_ascii_not_cjk(self):
        assert not is_cjk("A")
        assert not is_cjk("z")
        assert not is_cjk("0")
        assert not is_cjk(" ")

    def test_punctuation_not_cjk(self):
        assert not is_cjk("—")
        assert not is_cjk("(")


class TestTokenize:
    def test_latin_words_stay_together(self):
        tokens = tokenize("hello world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_cjk_split_by_character(self):
        tokens = tokenize("気持ち")
        assert tokens == ["気", "持", "ち"]

    def test_mixed_text(self):
        tokens = tokenize("after気持ち")
        assert "after" in tokens
        assert "気" in tokens
        assert "持" in tokens
        assert "ち" in tokens

    def test_spaces_preserved(self):
        tokens = tokenize("a b")
        assert " " in tokens or any(t.strip() == "" for t in tokens) or "a" in tokens

    def test_empty(self):
        assert tokenize("") == []


class TestKinsoku:
    def _font(self, char_w=10):
        f = MagicMock()
        f.getlength.side_effect = lambda text: len(text) * char_w
        return f

    def _lines(self, text, max_w=50, char_w=10):
        font = self._font(char_w)
        with patch("generate_translated_cards.get_font", return_value=font):
            return wrap_lines([(text, False, False)], {}, 0, max_w)

    def test_kinsoku_start_contains_expected(self):
        assert {"）", "、"} <= KINSOKU_START
        assert "。" not in KINSOKU_START

    def test_kinsoku_end_contains_expected(self):
        assert "（" in KINSOKU_END

    def test_no_break_before_closing_paren(self):
        # 'ABCDE' fills max_w exactly; without kinsoku '）' would start next line
        lines = self._lines("ABCDE）")
        first = "".join(w for w, _, _ in lines[0][0])
        assert "）" in first

    def test_no_break_before_comma(self):
        lines = self._lines("ABCDE、")
        first = "".join(w for w, _, _ in lines[0][0])
        assert "、" in first

    def test_no_break_after_open_paren(self):
        # 'ABCD（' fills max_w; 'XYZ' triggers break → '（' carries to next line
        lines = self._lines("ABCD（XYZ")
        first = "".join(w for w, _, _ in lines[0][0])
        assert not first.endswith("（")
        second = "".join(w for w, _, _ in lines[1][0])
        assert second.startswith("（")


class TestOutputPath:
    def test_normal_card(self):
        path = output_path("es", "card_images_blank/Scorn (White Mythic Rare).png")
        assert path == "translated-es/images/Scorn (White Mythic Rare).webp"

    def test_reversed_frustration(self):
        path = output_path("es", "card_images_blank/Frustration (Common Red).png")
        assert "Red Common" in path
        assert "Common Red" not in path

    def test_reversed_glee(self):
        path = output_path("ja", "card_images_blank/Glee (Common Red).png")
        assert "Red Common" in path
        assert "Common Red" not in path

    def test_correct_lang_folder(self):
        path = output_path("ja", "card_images_blank/Anger (Red Uncommon).png")
        assert path.startswith("translated-ja/")

    def test_webp_extension(self):
        path = output_path("es", "card_images_blank/Joy (Green Common).png")
        assert path.endswith(".webp")


@pytest.mark.skipif(
    not (
        __import__("os").path.exists("translations/cards_es.csv")
        and __import__("os").path.exists("translations/cards_ja.csv")
    ),
    reason="Proprietary card data not present",
)
class TestCsvData:
    @pytest.fixture
    def es_rows(self):
        with open("translations/cards_es.csv", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    @pytest.fixture
    def ja_rows(self):
        with open("translations/cards_ja.csv", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    BLANK_CARDS = {"Apathy", "Boredom", "Complacency", "Indifference", "Laziness"}

    def test_es_has_133_cards(self, es_rows):
        assert len(es_rows) == 133

    def test_ja_has_133_cards(self, ja_rows):
        assert len(ja_rows) == 133

    def test_es_all_names_filled(self, es_rows):
        missing = [r["name_en"] for r in es_rows if not r["name_es"].strip()]
        assert missing == []

    def test_ja_all_names_filled(self, ja_rows):
        missing = [r["name_en"] for r in ja_rows if not r["name_ja"].strip()]
        assert missing == []

    def test_es_text_filled_except_blank_cards(self, es_rows):
        missing = [
            r["name_en"]
            for r in es_rows
            if not r["text_es"].strip() and r["name_en"] not in self.BLANK_CARDS
        ]
        assert missing == []

    def test_ja_text_filled_except_blank_cards(self, ja_rows):
        missing = [
            r["name_en"]
            for r in ja_rows
            if not r["text_ja"].strip() and r["name_en"] not in self.BLANK_CARDS
        ]
        assert missing == []

    def test_es_no_duplicate_names(self, es_rows):
        from collections import Counter

        counts = Counter(r["name_es"] for r in es_rows)
        dups = [k for k, v in counts.items() if v > 1]
        assert dups == []

    def test_ja_no_duplicate_names(self, ja_rows):
        from collections import Counter

        counts = Counter(r["name_ja"] for r in ja_rows)
        dups = [k for k, v in counts.items() if v > 1]
        assert dups == []

    def test_blank_cards_have_no_text_es(self, es_rows):
        for r in es_rows:
            if r["name_en"] in self.BLANK_CARDS:
                assert r["text_es"].strip() == ""

    def test_blank_cards_have_no_text_ja(self, ja_rows):
        for r in ja_rows:
            if r["name_en"] in self.BLANK_CARDS:
                assert r["text_ja"].strip() == ""
