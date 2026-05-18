"""Generate blank card images by covering name and text areas."""

import glob
import os
import re
import subprocess

NAME_COLORS = {
    "White": "#959287",
    "Blue": "#0090D3",
    "Black": "#140027",
    "Red": "#CD3C36",
    "Green": "#029246",
}

BLANK_CARDS = {
    "White": "card_images/Complacency (White Common).webp",
    "Blue": "card_images/Indifference (Blue Common).webp",
    "Black": "card_images/Apathy (Black Common).webp",
    "Red": "card_images/Boredom (Red Common).webp",
    "Green": "card_images/Laziness (Green Common).webp",
}

# Coordinates (x1,y1 x2,y2)
NAME_COVER = (39, 39, 528, 121)
TEXT_COVER = (42, 604, 704, 944)

NAME_COVER_EXCEPTIONS = {
    "Rationalization": (39, 39, 545, 121),
}

# Dice in lower-left corner: restore these regions from the original after blanking
ONE_DIE_RESTORE  = (39,  852, 175, 963)
TWO_DICE_RESTORE = (9,   852, 238, 963)

ONE_DIE_CARDS = {
    "Ambivalence", "Animosity", "Cheer", "Chivalry", "Condescension",
    "Curiosity", "Cynicism", "Delight", "Determination", "Dignity",
    "Discipline", "Disgust", "Disregard", "Embarrassment", "Enjoyment",
    "Excitement", "Frustration", "Glee", "Loyalty", "Obsession",
    "Patience", "Pity", "Serenity", "Tranquility", "Triumph",
}

TWO_DICE_CARDS = {
    "Altruism", "Celebration", "Fascination", "Fondness", "Happiness",
    "Infatuation", "Love", "Misery", "Superiority", "Vulnerability",
}


def card_color(filename):
    m = re.search(r"\(([^)]+)\)", os.path.basename(filename))
    if not m:
        return None
    words = m.group(1).split()
    colors = {"White", "Blue", "Black", "Red", "Green"}
    for word in words:
        if word in colors:
            return word
    return None


def blank_card(src):
    basename = os.path.basename(src).replace(".webp", ".png")
    return os.path.join("card_images_blank", basename)


def generate(src):
    color = card_color(src)
    fill = NAME_COLORS[color]
    blank_src = BLANK_CARDS[color]

    x1, y1, x2, y2 = TEXT_COVER
    crop_w, crop_h = x2 - x1, y2 - y1

    name_en = re.match(r"^(.+?) \(", os.path.basename(src)).group(1)
    nc = NAME_COVER_EXCEPTIONS.get(name_en, NAME_COVER)

    out = blank_card(src)

    if name_en in TWO_DICE_CARDS:
        dice_restore = TWO_DICE_RESTORE
    elif name_en in ONE_DIE_CARDS:
        dice_restore = ONE_DIE_RESTORE
    else:
        dice_restore = None

    cmd = [
        "magick", src,
        "-fill", fill,
        "-draw", f"rectangle {nc[0]},{nc[1]} {nc[2]},{nc[3]}",
        "(", blank_src, "-crop", f"{crop_w}x{crop_h}+{x1}+{y1}", "+repage", ")",
        "-geometry", f"+{x1}+{y1}",
        "-composite",
    ]

    if dice_restore:
        dx1, dy1, dx2, dy2 = dice_restore
        dw, dh = dx2 - dx1, dy2 - dy1
        cmd += [
            "(", src, "-crop", f"{dw}x{dh}+{dx1}+{dy1}", "+repage", ")",
            "-geometry", f"+{dx1}+{dy1}",
            "-composite",
        ]

    cmd.append(out)
    subprocess.run(cmd, check=True)
    return out


def main():
    cards = sorted(glob.glob("card_images/*.webp"))
    total = len(cards)
    for i, src in enumerate(cards, 1):
        name = os.path.basename(src)
        out = generate(src)
        print(f"[{i:3d}/{total}] {name} → {out}")
    print(f"\nDone: {total} cards in card_images_blank/")


if __name__ == "__main__":
    main()
