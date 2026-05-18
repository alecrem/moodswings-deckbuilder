"""Render translated card names and text onto blank card images."""

import csv
import glob
import os
import re
import subprocess

from PIL import Image, ImageDraw, ImageFont

# Title fonts
FONT_NAME_ES = "fonts/Beleren2016SmallCaps-Bold.ttf"
FONT_NAME_JA = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

# Body text fonts
FONTS_ES = {
    "regular": "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "bold": "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "italic": "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
}
_MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
FONTS_JA = {
    "regular": (_MINCHO, 0),  # W3
    "bold": (_MINCHO, 2),  # W6
    "italic": (_MINCHO, 0),
}

NAME_POINTSIZE = 65
NAME_X, NAME_Y = 59, 62
NAME_COLOR = "white"

TEXT_X1, TEXT_Y1 = 64, 642
TEXT_X2, TEXT_Y2 = 680, 906
TEXT_W = TEXT_X2 - TEXT_X1  # 616
TEXT_H_DEFAULT = TEXT_Y2 - TEXT_Y1  # 264
TEXT_H_DICE = 842 - TEXT_Y1  # 200 — stop before lower-left dice

TEXT_MAX_SIZE = 40
TEXT_COLOR = (0, 0, 0)
PARA_SPACING = 0.35  # extra fraction of line_height between paragraphs

ONE_DIE_CARDS = {
    "Ambivalence",
    "Animosity",
    "Cheer",
    "Chivalry",
    "Condescension",
    "Curiosity",
    "Cynicism",
    "Delight",
    "Determination",
    "Dignity",
    "Discipline",
    "Disgust",
    "Disregard",
    "Embarrassment",
    "Enjoyment",
    "Excitement",
    "Frustration",
    "Glee",
    "Loyalty",
    "Obsession",
    "Patience",
    "Pity",
    "Serenity",
    "Tranquility",
    "Triumph",
}
TWO_DICE_CARDS = {
    "Altruism",
    "Celebration",
    "Fascination",
    "Fondness",
    "Happiness",
    "Infatuation",
    "Love",
    "Misery",
    "Superiority",
    "Vulnerability",
}


# ── Rich text rendering ──────────────────────────────────────────────────────

KINSOKU_START = frozenset("）、")  # cannot start a line
KINSOKU_END = frozenset("（")  # cannot end a line


def parse_segments(html):
    segments = []
    bold = italic = False
    for part in re.split(r"(<[^>]+>)", html):
        if part == "<strong>":
            bold = True
        elif part == "</strong>":
            bold = False
        elif re.match(r"<em\s*>", part):
            italic = True
        elif re.match(r"</em\s*>", part):
            italic = False
        elif re.match(r"<br\s*/?>", part):
            segments.append(("\x00para", False, False))
        elif not part.startswith("<") and part:
            segments.append((part, bold, italic))
    return segments


def load_font(spec, size):
    if isinstance(spec, tuple):
        return ImageFont.truetype(spec[0], size, index=spec[1])
    return ImageFont.truetype(spec, size)


def get_font(fonts, bold, italic, size):
    key = "bold" if bold else ("italic" if italic else "regular")
    return load_font(fonts.get(key, fonts["regular"]), size)


def lh(font):
    m = font.getmetrics()
    return m[0] + m[1]


def is_cjk(ch):
    return "　" <= ch <= "鿿" or "豈" <= ch <= "￯" or "　0" <= ch <= "㿿f"


def tokenize(text):
    """Split on whitespace; also split each CJK character individually."""
    tokens = []
    for part in re.split(r"(\s+)", text):
        if not part:
            continue
        chunk = ""
        for ch in part:
            if is_cjk(ch):
                if chunk:
                    tokens.append(chunk)
                    chunk = ""
                tokens.append(ch)
            else:
                chunk += ch
        if chunk:
            tokens.append(chunk)
    return tokens


def wrap_lines(segments, fonts, size, max_w):
    """Return list of (line_segments, is_para_break)."""
    lines, cur, cur_w = [], [], 0
    for text, b, i in segments:
        font = get_font(fonts, b, i, size)
        if text == "\x00para":
            lines.append((cur, True))
            cur, cur_w = [], 0
            continue
        for word in tokenize(text):
            if not word:
                continue
            w = font.getlength(word)
            if cur_w + w > max_w and cur:
                if word[0] in KINSOKU_START:
                    # Don't break before ）、
                    cur.append((word, b, i))
                    cur_w += w
                    continue
                if cur[-1][0] and cur[-1][0][-1] in KINSOKU_END:
                    # Don't break after （ — move it to start of next line
                    carried, cb, ci = cur.pop()
                    cur_w -= get_font(fonts, cb, ci, size).getlength(carried)
                    lines.append((cur, False))
                    cur = [(carried, cb, ci)]
                    cur_w = get_font(fonts, cb, ci, size).getlength(carried)
                else:
                    lines.append((cur, False))
                    cur, cur_w = [], 0
                word = word.lstrip()
                if not word:
                    continue
                w = font.getlength(word)
            cur.append((word, b, i))
            cur_w += w
    if cur:
        lines.append((cur, False))
    return lines


def total_h(lines, line_h):
    return sum(line_h + (line_h * PARA_SPACING if pb else 0) for _, pb in lines)


ITALIC_SHEAR = 0.22  # tan(~12°)


def draw_word_italic(img, word, font, x, y):
    """Render word with synthetic italic shear onto img."""
    bbox = font.getbbox(word)
    w = max(bbox[2] - bbox[0], 1)
    bot = max(bbox[3], 1)  # full height from origin keeps 。ー vertically aligned
    pad = int(bot * ITALIC_SHEAR) + 2

    tmp = Image.new("RGBA", (w + pad + 2, bot + 4), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((-bbox[0] + pad, 0), word, font=font, fill=TEXT_COLOR)
    sheared = tmp.transform(
        (w + pad + 2, bot + 4),
        Image.AFFINE,
        (1, ITALIC_SHEAR, 0, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    img.paste(sheared, (int(x) - pad, int(y)), sheared)


def render_body(html, fonts, max_size, width, height, synthetic_italic=False):
    html = html.replace("。）", "）")
    segs = parse_segments(html)
    lo, hi, best = 9, max_size, 9
    while lo <= hi:
        mid = (lo + hi) // 2
        lines = wrap_lines(segs, fonts, mid, width)
        line_h = lh(get_font(fonts, False, False, mid))
        if lines and total_h(lines, line_h) <= height:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    lines = wrap_lines(segs, fonts, best, width)
    line_h = lh(get_font(fonts, False, False, best))
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = 0
    for line_segs, is_para_break in lines:
        line_w = sum(get_font(fonts, b, i, best).getlength(w) for w, b, i in line_segs)
        x = (width - line_w) / 2
        for word, b, i in line_segs:
            font = get_font(fonts, b, i, best)
            if i and synthetic_italic:
                draw_word_italic(img, word, font, x, y)
            else:
                draw.text((x, y), word, font=font, fill=TEXT_COLOR)
            x += font.getlength(word)
        y += line_h + (line_h * PARA_SPACING if is_para_break else 0)
    return img


# ── Card generation ──────────────────────────────────────────────────────────


def find_blank(name_en):
    matches = glob.glob(f"card_images_blank/{name_en} (*).png")
    return matches[0] if matches else None


def output_path(lang, blank_src):
    basename = os.path.basename(blank_src).replace(".png", ".webp")
    # Normalise reversed "Common Red" → "Red Common" to match HTML expectations
    basename = re.sub(
        r"\((Common) (Red|Green|Blue|Black|White)\)", r"(\2 \1)", basename
    )
    return os.path.join(f"translated-{lang}", "images", basename)


def render_card(blank_src, name_translated, text_translated, lang, name_en, out_path):
    font_name = FONT_NAME_ES if lang == "es" else FONT_NAME_JA
    fonts_body = FONTS_ES if lang == "es" else FONTS_JA

    has_dice = name_en in ONE_DIE_CARDS or name_en in TWO_DICE_CARDS
    text_h = TEXT_H_DICE if has_dice else TEXT_H_DEFAULT

    # Load blank, render title
    base = Image.open(blank_src).convert("RGBA")
    tmp_title = "/tmp/ms_title_tmp.png"
    subprocess.run(
        [
            "magick",
            blank_src,
            "-font",
            font_name,
            "-pointsize",
            str(NAME_POINTSIZE),
            "-fill",
            NAME_COLOR,
            "-gravity",
            "NorthWest",
            "-annotate",
            f"+{NAME_X}+{NAME_Y}",
            name_translated,
            tmp_title,
        ],
        check=True,
    )
    base = Image.open(tmp_title).convert("RGBA")

    # Render body text
    body = text_translated.strip()
    if body:
        text_img = render_body(
            body,
            fonts_body,
            TEXT_MAX_SIZE,
            TEXT_W,
            text_h,
            synthetic_italic=(lang == "ja"),
        )
        base.paste(text_img, (TEXT_X1, TEXT_Y1), text_img)

    base.convert("RGB").save(out_path)


def main():
    import sys

    filter_lang = sys.argv[1] if len(sys.argv) > 1 else None

    all_langs = [
        ("es", "translations/cards_es.csv", "name_es", "text_es"),
        ("ja", "translations/cards_ja.csv", "name_ja", "text_ja"),
    ]
    for lang, csv_file, name_col, text_col in all_langs:
        if filter_lang and lang != filter_lang:
            continue
        os.makedirs(f"translated-{lang}/images", exist_ok=True)

        with open(csv_file, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        total = len(rows)
        for i, row in enumerate(rows, 1):
            name_en = row["name_en"]
            name_tr = row[name_col]
            text_tr = row[text_col]

            blank = find_blank(name_en)
            if not blank:
                print(f"  [MISSING blank] {name_en}")
                continue

            out = output_path(lang, blank)
            render_card(blank, name_tr, text_tr, lang, name_en, out)
            print(f"[{lang}] [{i:3d}/{total}] {name_en} → {name_tr}")

        print(f"\nDone [{lang}]: {total} cards\n")


if __name__ == "__main__":
    main()
