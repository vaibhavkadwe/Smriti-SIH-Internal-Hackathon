#!/usr/bin/env python3
"""Generate Monad-style PWA icons for Smriti.

Parchment (#f6f3f1) background, centered lake-blue (#2b59d1) serif "S"
monogram inside a thin pill outline — the system's container language.
Outputs: icon-192.png, icon-512.png, icon-512-maskable.png (80% safe zone).
"""
from PIL import Image, ImageDraw, ImageFont

PARCHMENT = (246, 243, 241)
LAKE_BLUE = (43, 89, 209)
ASH = (206, 202, 200)

OUT = "public/icons"


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """Georgia first (matches the app's serif stack), then common fallbacks."""
    for path in (
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Georgia.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_icon(size: int, maskable: bool = False) -> Image.Image:
    img = Image.new("RGB", (size, size), PARCHMENT)
    d = ImageDraw.Draw(img)

    # Maskable icons: content must live inside the inner 80% safe zone
    # (Android masks ~10% off each edge). Non-maskable centers freely.
    inset = int(size * 0.10) if maskable else 0
    s = size - 2 * inset  # usable canvas
    cx, cy = size / 2, size / 2

    # Thin pill outline (ash hairline) — Monad's border language, scaled.
    outline_w = max(2, size // 170)
    pill_pad = s * 0.06
    pill_w = s * 0.52
    pill_h = s * 0.78
    d.rounded_rectangle(
        [cx - pill_w / 2 - pill_pad, cy - pill_h / 2 - pill_pad,
         cx + pill_w / 2 + pill_pad, cy + pill_h / 2 + pill_pad],
        radius=(pill_h + 2 * pill_pad) / 2,
        outline=ASH, width=outline_w,
    )

    # Serif monogram — weight 400 look (default weights only here; the serif
    # stroke contrast carries the identity, per DESIGN.md).
    font = load_font(int(s * 0.42))
    bbox = d.textbbox((0, 0), "S", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), "S",
           font=font, fill=LAKE_BLUE)

    return img


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    draw_icon(192).save(f"{OUT}/icon-192.png")
    draw_icon(512).save(f"{OUT}/icon-512.png")
    draw_icon(512, maskable=True).save(f"{OUT}/icon-512-maskable.png")
    print("wrote", OUT + "/icon-{192,512,512-maskable}.png")
