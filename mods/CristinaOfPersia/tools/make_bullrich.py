#!/usr/bin/env python3
"""Sprites alternativos del protagonista: Bullrich borracha.

Cuando Cristina toma una poción, el juego la muestra un rato con estos sprites
y la hace tambalear (ver add_kid_to_objtable en src/seg008.c). Van en
data/KID/res1401-1619 (el mismo frame que res401-619, más 1000) con un
res1400.pal que describe el set.

- Pelo corto rubio, tipo carré hasta la mandíbula
- Campera de cuero negra con mangas largas (quedan las manos)
- Jean azul
- Zapatos negros
- Nariz y cachete colorados
"""
import os, glob, shutil
from PIL import Image
from make_kid import (components, sleeves, T, HAIR, EYE, HAIR_D, SKIN_D, SKIN,
                      CLOTH_EDGE, CLOTH, FOOT_A, FOOT_B, SLEEVE_D, LIPS)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "KID")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "KID")
OFFSET = 1000

JEANS, JEANS_D = 11, 10
NOSE = LIPS

COLORS = {
    HAIR: (220, 192, 128),
    HAIR_D: (164, 132, 78),
    CLOTH: (32, 30, 36),         # cuero
    CLOTH_EDGE: (104, 100, 112),  # brillo del cuero
    SLEEVE_D: (16, 14, 18),
    EYE: (70, 40, 40),
    NOSE: (232, 64, 76),
    FOOT_A: (34, 30, 30),
    FOOT_B: (18, 16, 16),
    JEANS: (62, 88, 148),
    JEANS_D: (38, 56, 104),
}
BOB = 2          # filas que baja el pelo por la nuca
WAIST = 14       # filas desde el fin del pelo hasta la cintura


def transform(im):
    im = im.copy()
    w, h = im.size
    px = im.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == JEANS_D:      # único uso: duplicado del ojo
                px[x, y] = EYE
            elif px[x, y] == SLEEVE_D:
                px[x, y] = CLOTH_EDGE
            elif px[x, y] == NOSE:
                px[x, y] = SKIN

    comps = components(px, w, h, {HAIR, HAIR_D})
    hair_px = [p for c in comps if len(c) >= 12 for p in c]
    for c in comps:  # el cinturón dorado pasa a ser un cinturón negro
        if 3 <= len(c) < 12:
            for p in c:
                px[p] = FOOT_B
    if hair_px:
        hy = [p[1] for p in hair_px]
        cx = sum(p[0] for p in hair_px) / len(hair_px)
        top, bottom = min(hy), max(hy)
        face = [(x, y) for y in range(top, min(h, bottom + 3)) for x in range(w)
                if px[x, y] in (SKIN, SKIN_D, EYE)]
        back = 1 if not face or sum(p[0] for p in face) / len(face) < cx else -1

        # jean de la cintura para abajo (antes de las mangas, que son de cuero)
        waist = bottom + WAIST
        for y in range(waist, h):
            for x in range(w):
                if px[x, y] == CLOTH:
                    px[x, y] = JEANS
                elif px[x, y] == CLOTH_EDGE:
                    px[x, y] = JEANS_D

        # carré: el pelo de la nuca baja un poco
        cols = {}
        for x, y in hair_px:
            if (x - cx) * back >= 0:
                cols[x] = max(cols.get(x, -1), y)
        for x, yb in cols.items():
            for dy in range(1, BOB + 1):
                y = yb + dy
                if y < h and px[x, y] in (T, CLOTH, CLOTH_EDGE):
                    px[x, y] = HAIR_D if dy == BOB else HAIR

        sleeves(px, w, h, hair_px, back, bottom)

        # nariz y cachete colorados
        eyes = [(x, y) for y in range(top, min(h, bottom + 2)) for x in range(w) if px[x, y] == EYE]
        if len(eyes) == 1:
            ex, ey = eyes[0]
            y = ey + 1
            if y < h:
                row = [x for x in range(w) if px[x, y] in (SKIN, SKIN_D) and abs(x - ex) <= 3]
                if row:
                    nose = min(row) if back > 0 else max(row)
                    px[nose, y] = NOSE
                    cheek = nose + 2 * back
                    if 0 <= cheek < w and px[cheek, y] in (SKIN, SKIN_D):
                        px[cheek, y] = NOSE

    pal = im.getpalette()
    pal = pal + [0] * (768 - len(pal))
    for i, rgb in COLORS.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    return im


def main():
    os.makedirs(DST, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "res*.png")))
    for f in files:
        n = int(os.path.basename(f)[3:-4])
        transform(Image.open(f)).save(os.path.join(DST, f"res{n + OFFSET}.png"))
    shutil.copy(os.path.join(SRC, "res400.pal"), os.path.join(DST, f"res{400 + OFFSET}.pal"))
    print(f"{len(files)} frames -> {DST} (res{401 + OFFSET}-{400 + OFFSET + len(files)})")


if __name__ == "__main__":
    main()
