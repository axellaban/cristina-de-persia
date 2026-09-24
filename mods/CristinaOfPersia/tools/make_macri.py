#!/usr/bin/env python3
"""Convierte a Jafar (el visir) en Macri, el villano.

Aplica a las escenas (data/PV/res851-888) y a la pelea final del nivel 13
(data/VIZIER/res751-784).

- Turbante -> pelo corto canoso con entradas (el resto del turbante se borra)
- Cara: piel clara, ojo celeste, bigote
- Barba blanca -> cuello de camisa blanca
- Túnica blanca -> saco azul marino largo
- Pantalón rosa -> pantalón gris oscuro
- Zapatos dorados -> zapatos negros
- Corbata amarilla (PRO)

Los globos amarillos que suben cuando entra en escena los dibuja el juego
(draw_balloons en src/seg001.c) con PV/res963, que genera este script.

Mantiene el tamaño exacto de cada imagen.
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

T = 0
PANTS, PANTS_D, WHITE, EYE, SKIN_D, SKIN, BEARD, ROBE_D, ROBE = 1, 2, 3, 4, 5, 6, 7, 8, 9
SHOE_D, SHOE, TURBAN, TURBAN2, TIE, TURBAN_O = 10, 11, 12, 13, 14, 15
HAIR, HAIR_D, MUSTACHE = TURBAN, TURBAN_O, TURBAN2

NEW_COLORS = {
    PANTS: (52, 54, 72),
    PANTS_D: (34, 36, 50),
    WHITE: (250, 250, 250),
    EYE: (96, 170, 236),
    SKIN_D: (206, 156, 128),
    SKIN: (240, 196, 168),
    BEARD: (250, 250, 250),
    ROBE_D: (18, 22, 56),
    ROBE: (30, 38, 92),
    SHOE_D: (58, 50, 50),
    SHOE: (26, 22, 22),
    HAIR: (178, 170, 160),
    HAIR_D: (122, 114, 106),
    MUSTACHE: (96, 80, 68),
    TIE: (250, 212, 0),       # amarillo PRO
}
TIE_LEN = 13
SUIT = (ROBE, ROBE_D, PANTS, PANTS_D)
TURBANS = (TURBAN, TURBAN2, TURBAN_O)


def haircut(px, w, h, turban, eye, back):
    """Pelo corto alrededor de la cabeza; el resto del turbante desaparece."""
    ex, ey = eye
    for x, y in turban:
        b = (x - ex) * back  # 0 = frente, crece hacia la nuca
        keep = False
        if ey - 3 <= y <= ey and 0 <= b <= 6:
            keep = not (y == ey - 3 and b in (0, 6))  # esquinas redondeadas
        elif y == ey + 1 and 3 <= b <= 5:
            keep = True  # nuca
        px[x, y] = (HAIR_D if b >= 5 or y == ey + 1 else HAIR) if keep else T
    # entradas: la frente queda despejada
    for y, bs in ((ey - 1, (0, 1)), (ey - 2, (0,))):
        for b in bs:
            x = ex + b * back
            if 0 <= x < w and 0 <= y < h and px[x, y] in (HAIR, HAIR_D, T):
                px[x, y] = SKIN


def mustache(px, w, h, eye, back):
    ex, ey = eye
    y = ey + 2
    if y >= h:
        return
    row = [x for x in range(w) if px[x, y] in (SKIN, SKIN_D) and abs(x - ex) <= 3]
    if row:
        x0 = min(row) if back > 0 else max(row)  # lo más adelantado
        for k in range(2):
            x = x0 + k * back
            if 0 <= x < w and px[x, y] in (SKIN, SKIN_D):
                px[x, y] = MUSTACHE


def transform(im):
    im = im.copy()
    w, h = im.size
    px = im.load()
    turban = [(x, y) for y in range(h) for x in range(w) if px[x, y] in TURBANS]
    face = [(x, y) for y in range(h) for x in range(w) if px[x, y] in (SKIN, SKIN_D, EYE)]
    # el índice 13 del turbante pasa a ser el bigote: se unifica antes
    for x, y in turban:
        px[x, y] = TURBAN
    if turban:
        top = min(p[1] for p in turban)
        # el fajín de la cintura también era color turbante -> cinturón oscuro
        for x, y in turban:
            if y > top + 8:
                px[x, y] = PANTS_D
        turban = [p for p in turban if p[1] <= top + 8]
    if turban and face:
        hx = sum(p[0] for p in turban) / len(turban)
        fx = sum(p[0] for p in face) / len(face)
        back = 1 if fx < hx else -1
        # la cara está justo debajo del turbante (las manos levantadas no cuentan)
        tx0, tx1 = min(p[0] for p in turban) - 3, max(p[0] for p in turban) + 3
        head_face = [p for p in face if top + 3 <= p[1] <= top + 9 and tx0 <= p[0] <= tx1]
        eyes = [(x, y) for x, y in head_face if px[x, y] == EYE]
        if eyes:
            eye = eyes[0]
        elif head_face:
            fy = min(p[1] for p in head_face)
            row = [x for x, y in head_face if y == fy]
            eye = (min(row) if back > 0 else max(row), fy)
        else:
            eye = None
        if eye:
            haircut(px, w, h, turban, eye, back)
            mustache(px, w, h, eye, back)
        front = -back
        fbottom = max(p[1] for p in head_face) if head_face else top + 7
        ffront = (max if front > 0 else min)(p[0] for p in head_face) if head_face else round(fx)
        # la barba que toca la cara es mentón; justo debajo, cuello de camisa;
        # más abajo el gris claro era el forro de la túnica -> forro oscuro
        for y in range(h):
            for x in range(w):
                if px[x, y] == BEARD:
                    if y <= fbottom:
                        px[x, y] = SKIN
                    elif y > fbottom + 3:
                        px[x, y] = ROBE_D
        # corbata recta, colgando del cuello
        collar = [(x, y) for y in range(h) for x in range(w) if px[x, y] == BEARD]
        start = (max(p[1] for p in collar) + 1) if collar else fbottom + 2
        tx = ffront - front * 2
        painted = 0
        for k in range(TIE_LEN + 4):
            y = start + k
            if y >= h or painted >= TIE_LEN:
                break
            if 0 <= tx < w and px[tx, y] in SUIT:
                px[tx, y] = TIE
                painted += 1
                if painted == 1:  # nudo
                    x2 = tx - front
                    if 0 <= x2 < w and px[x2, y] in SUIT:
                        px[x2, y] = TIE
            elif painted:
                break
    elif turban:
        # de espaldas: sólo la coronilla
        top = min(p[1] for p in turban)
        cx = sum(p[0] for p in turban) / len(turban)
        for x, y in turban:
            px[x, y] = HAIR if top + 2 <= y <= top + 5 and abs(x - cx) <= 3 else T
    pal = im.getpalette()
    pal = pal + [0] * (768 - len(pal))
    for i, rgb in NEW_COLORS.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    return im


BALLOON = [
    "...yyyyy...",
    "..yYYyyyy..",
    ".yYYyyyyyy.",
    ".yYyyyyyyyo",
    "yyyyyyyyyyo",
    "yyyyyyyyyyo",
    "yyyyyyyyyyo",
    ".yyyyyyyyo.",
    ".yyyyyyyoo.",
    "..yyyyyoo..",
    "...yyoo....",
    "....oo.....",
    ".....s.....",
    "....s......",
    "....s......",
    ".....s.....",
    "......s....",
    "......s....",
    ".....s.....",
]
BALLOON_COLORS = {".": (0, 0, 0), "y": (252, 214, 0), "Y": (255, 246, 170),
                  "o": (206, 158, 0), "s": (230, 230, 230)}


def balloon():
    """Globo amarillo del PRO, para los globos que suben en la escena (res963)."""
    keys = list(BALLOON_COLORS)
    im = Image.new("P", (len(BALLOON[0]), len(BALLOON)), 0)
    pal = [c for k in keys for c in BALLOON_COLORS[k]]
    im.putpalette(pal + [0] * (768 - len(pal)))
    for y, row in enumerate(BALLOON):
        for x, ch in enumerate(row):
            im.putpixel((x, y), keys.index(ch))
    dst = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "PV")
    im.save(os.path.join(dst, "res963.png"), transparency=0)
    # la paleta del cuarto de la princesa, con una imagen más (el globo)
    pal = bytearray(open(os.path.join(ROOT, "data", "PV", "res950.pal"), "rb").read())
    pal[0] = 13
    open(os.path.join(dst, "res950.pal"), "wb").write(pal)
    print("globo -> PV/res963.png")


def run(folder, ids):
    src = os.path.join(ROOT, "data", folder)
    dst = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", folder)
    os.makedirs(dst, exist_ok=True)
    for i in ids:
        name = f"res{i}.png"
        transform(Image.open(os.path.join(src, name))).save(os.path.join(dst, name))
    print(f"{len(ids)} frames -> {dst}")


def main():
    run("PV", range(851, 889))
    run("VIZIER", range(751, 785))
    balloon()


if __name__ == "__main__":
    main()
