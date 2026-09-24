#!/usr/bin/env python3
"""Los guardias pasan a ser Granaderos (la guardia presidencial).

Los sprites de los guardias vienen en escala de grises y el juego los pinta
con una de 7 paletas según el nivel (data/PRINCE/res10.bin, 16 colores VGA de
6 bits cada una). Acá se reescriben esas paletas:

- casaca azul oscuro, pantalón blanco, correaje blanco, morrión negro, botas negras
- el color del penacho/vivos cambia con la paleta, para que se sigan
  distinguiendo los guardias más fuertes

Además se redibuja la cabeza de los guardias (data/GUARD) y del guardia gordo
(data/FAT): el turbante pasa a ser el morrión alto de los Granaderos, con visera y
penacho, pelo corto en la nuca y cuello del color de los vivos. Las imágenes crecen
hacia arriba (el juego las apoya por abajo, así que el guardia no se mueve).
"""
import os, glob
from PIL import Image
from make_kid import components

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "PRINCE", "res10.bin")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "PRINCE", "res10.bin")

# vivos del uniforme por paleta (1..7)
TRIMS = [
    (200, 30, 40),    # rojo
    (230, 180, 40),   # dorado
    (110, 180, 236),  # celeste
    (200, 30, 40),
    (240, 240, 240),  # blanco
    (230, 180, 40),
    (200, 30, 40),
]


def palette(trim):
    return [
        (0, 0, 0),         # 0 transparente
        (226, 226, 232),   # 1 pantalón
        (168, 168, 184),   # 2 pantalón sombra
        (22, 22, 28),      # 3 morrión
        None, None, None,  # 4-6 piel: se deja la original
        (70, 86, 170),     # 7 casaca brillo
        (18, 24, 70),      # 8 casaca sombra
        (32, 42, 112),     # 9 casaca
        (60, 56, 56),      # 10 botas brillo
        (26, 22, 22),      # 11 botas
        (240, 240, 240),   # 12 correaje / cinturón
        (168, 168, 184),   # 13 pantalón sombra (duplicado)
        trim,              # 14 vivos del morrión
        None,              # 15 sangre: se deja la original
    ]


# índices de los sprites de guardia (el juego les pone la paleta de arriba)
SHAKO, TRIM, CORD = 3, 14, 12
SKIN_G = (4, 5, 6)
COAT = (7, 8, 9)
SHAKO_H = 7      # alto del morrión (sin el penacho)
SHAKO_W = 6
PLUME_H = 4


def shako(im, turban_idx, shade_idx=None):
    w, h = im.size
    px = im.load()
    opaque = [(x, y) for y in range(h) for x in range(w) if px[x, y]]
    if not opaque:
        return im
    top0 = min(p[1] for p in opaque)
    comps = [c for c in components(px, w, h, set(turban_idx)) if min(p[1] for p in c) <= top0 + 2]
    if not comps:
        return im
    turban = [p for c in comps for p in c]
    tx0, tx1 = min(p[0] for p in turban), max(p[0] for p in turban)
    ty1 = max(p[1] for p in turban)
    if shade_idx is not None:  # sombra del turbante que también se usa en la ropa
        turban += [(x, y) for y in range(top0, ty1 + 1) for x in range(tx0, tx1 + 1)
                   if px[x, y] == shade_idx]
    face = [(x, y) for y in range(top0, min(h, ty1 + 3)) for x in range(tx0 - 3, tx1 + 4)
            if 0 <= x < w and px[x, y] in SKIN_G]
    if len(face) < 4:
        return im  # de espaldas o caído: queda como está
    tcx = sum(p[0] for p in turban) / len(turban)
    fcx = sum(p[0] for p in face) / len(face)
    front = -1 if fcx < tcx else 1
    face_top = min(p[1] for p in face)
    face_front = (min if front < 0 else max)(p[0] for p in face)
    face_back = (max if front < 0 else min)(p[0] for p in face if p[1] == face_top)

    # filas que se agregan arriba para que entren el morrión y el penacho
    PAD = max(0, SHAKO_H + PLUME_H - face_top)
    out = Image.new("P", (w, h + PAD), 0)
    out.putpalette(im.getpalette())
    out.paste(im, (0, PAD))
    o = out.load()
    # el turbante: lo que está a la altura de la cara y pegado a la nuca es pelo corto;
    # el resto se borra y en su lugar va el morrión
    for x, y in turban:
        behind = (x - face_back) * -front
        keep_hair = y >= face_top and 0 <= behind <= 2
        o[x, y + PAD] = SHAKO if keep_hair else 0
    bottom = face_top - 1 + PAD
    x_front = face_front + front  # la visera asoma por delante de la frente
    for k in range(SHAKO_H):
        y = bottom - k
        # un poco más ancho arriba, como el morrión
        width = SHAKO_W + (1 if k >= SHAKO_H - 3 else 0)
        for i in range(width):
            x = x_front - front * (i + (0 if k == 0 else 1))
            if 0 <= x < w and 0 <= y:
                o[x, y] = SHAKO
        if k == 0 and 0 <= x_front < w:
            o[x_front, y] = SHAKO  # visera
    # cordón blanco cruzado y penacho del color de los vivos
    for k in range(3):
        x = x_front - front * (2 + k)
        y = bottom - 1 - k
        if 0 <= x < w:
            o[x, y] = CORD
    ptop = bottom - SHAKO_H + 1
    for dy, dxs in ((-1, (2, 3)), (-2, (2, 3)), (-3, (2, 3)), (-4, (3,))):
        for dx in dxs:
            x, y = x_front - front * dx, ptop + dy
            if 0 <= x < w and 0 <= y:
                o[x, y] = TRIM
    # cuello de la casaca del color de los vivos
    face2 = [(x, y + PAD) for x, y in face]
    neck_y = max(p[1] for p in face2) + 1
    ncx = sum(p[0] for p in face2) / len(face2)
    for y in (neck_y, neck_y + 1):
        if y >= h + PAD:
            continue
        for x in range(w):
            if o[x, y] in COAT and abs(x - ncx) <= 2:
                o[x, y] = TRIM
    return out


def heads(folder, turban_idx, palette_for_png=None, shade_idx=None):
    src = os.path.join(ROOT, "data", folder)
    dst = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", folder)
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(src, "res*.png"))):
        im = shako(Image.open(f), turban_idx, shade_idx)
        if palette_for_png:
            pal = (im.getpalette() + [0] * 768)[:768]
            for k, rgb in enumerate(palette_for_png):
                if rgb is not None:
                    pal[k * 3:k * 3 + 3] = rgb
            im.putpalette(pal)
        im.save(os.path.join(dst, os.path.basename(f)), transparency=0)
        n += 1
    print(f"{n} cabezas de Granadero -> {dst}")


def main():
    heads("GUARD", (SHAKO, TRIM))
    # el guardia gordo trae su propia paleta en los PNG: se le pone la de Granadero
    heads("FAT", (SHAKO,), palette(TRIMS[0]), shade_idx=7)
    data = bytearray(open(SRC, "rb").read())
    n = len(data) // 48
    for g in range(n):
        for k, rgb in enumerate(palette(TRIMS[g % len(TRIMS)])):
            if rgb is None:
                continue
            for c in range(3):
                data[g * 48 + k * 3 + c] = rgb[c] >> 2  # VGA de 6 bits
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "wb").write(data)
    print(f"{n} paletas de guardia -> {DST}")


if __name__ == "__main__":
    main()
