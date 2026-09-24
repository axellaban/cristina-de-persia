#!/usr/bin/env python3
"""Los guardias pasan a ser bufones, como el comodín de la baraja.

- Gorro de bufón de dos colores con dos puntas caídas y un cascabel dorado en cada una
- Gorguera blanca en el cuello
- Jubón rojo con rombos de arlequín; el color de los rombos (y de medio gorro)
  cambia con la paleta del guardia, así se siguen distinguiendo los más fuertes
- Mangas y calzas amarillas, cinturón dorado
- Zapatos puntiagudos con la punta enroscada y un cascabel
- En la mano, una trompeta en lugar de la espada (make_trumpet.py)

Los sprites de los guardias vienen en escala de grises y el juego los pinta con una
de 7 paletas según el guardia (data/PRINCE/res10.bin, 16 colores VGA de 6 bits cada
una). Acá se reescriben esas paletas y se reasignan los índices de cada sprite:

    1 / 2  calzas y mangas (y su sombra)        10  dorado: cascabeles y cinturón
    3      sombra de la gorguera                11  zapatos
    4-6    piel (la original)                   12  rombos en la sombra
    7/8/9  jubón rojo (brillo / sombra / base)  13  gorguera
    14     rombos y medio gorro                 15  sangre (la original)

El guardia gordo (data/FAT) trae la paleta en sus PNG: se le pone la de bufón.
Las imágenes crecen sólo hacia arriba: el juego apoya los sprites por abajo y por la
izquierda (y usa el ancho para los choques), así que el ancho no cambia.
"""
import os
import glob
from PIL import Image
from make_kid import components

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC_PAL = os.path.join(ROOT, "data", "PRINCE", "res10.bin")
DST_PAL = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "PRINCE", "res10.bin")

T = 0
TIGHTS, TIGHTS_D = 1, 2
RUFF_D = 3
SKIN = (4, 5, 6)
TUNIC_HI, TUNIC_D, TUNIC = 7, 8, 9
GOLD, SHOE = 10, 11
MOTLEY_D, RUFF, MOTLEY = 12, 13, 14

# índices originales
O_TIGHTS, O_TIGHTS_D, O_TURBAN, O_ROBE_HI, O_ROBE_D, O_ROBE = 1, 2, 3, 7, 8, 9
O_SHOE_HI, O_SHOE, O_SASH, O_TIGHTS_D2, O_TURBAN_D = 10, 11, 12, 13, 14

# color de los rombos por paleta (1..7): uno distinto para cada tipo de guardia
MOTLEYS = [
    ((40, 36, 52), (20, 18, 28)),       # negro
    ((56, 168, 76), (30, 104, 44)),     # verde
    ((96, 176, 244), (52, 112, 176)),   # celeste
    ((244, 244, 244), (176, 176, 190)), # blanco
    ((150, 76, 210), (92, 42, 136)),    # violeta
    ((40, 36, 52), (20, 18, 28)),       # negro
    ((56, 168, 76), (30, 104, 44)),     # verde
]


def palette(motley):
    m, md = motley
    return [
        (0, 0, 0),          # 0 transparente
        (240, 200, 56),     # 1 calzas y mangas
        (184, 136, 28),     # 2 su sombra
        (184, 184, 200),    # 3 sombra de la gorguera
        None, None, None,   # 4-6 piel: la original
        (240, 86, 80),      # 7 jubón brillo
        (124, 18, 36),      # 8 jubón sombra
        (200, 34, 48),      # 9 jubón
        (252, 212, 60),     # 10 dorado
        (60, 32, 70),       # 11 zapatos
        md,                 # 12 rombos en la sombra
        (248, 248, 248),    # 13 gorguera
        m,                  # 14 rombos
        None,               # 15 sangre: la original
    ]


CELL = 6  # tamaño de los rombos


def head_info(px, w, h, turban_idx, shade_idx):
    opaque = [(x, y) for y in range(h) for x in range(w) if px[x, y]]
    if not opaque:
        return None
    top0 = min(p[1] for p in opaque)
    comps = [c for c in components(px, w, h, set(turban_idx)) if min(p[1] for p in c) <= top0 + 2]
    if not comps:
        return None
    turban = [p for c in comps for p in c]
    tx0, tx1 = min(p[0] for p in turban), max(p[0] for p in turban)
    ty1 = max(p[1] for p in turban)
    if shade_idx is not None:
        turban += [(x, y) for y in range(top0, ty1 + 1) for x in range(tx0, tx1 + 1)
                   if px[x, y] == shade_idx]
    face = [(x, y) for y in range(top0, min(h, ty1 + 4)) for x in range(tx0 - 3, tx1 + 4)
            if 0 <= x < w and px[x, y] in SKIN]
    tcx = sum(p[0] for p in turban) / len(turban)
    if len(face) < 4:
        return dict(turban=set(turban), face=None, tcx=tcx, top=min(p[1] for p in turban))
    fcx = sum(p[0] for p in face) / len(face)
    return dict(turban=set(turban), face=face, tcx=tcx, fcx=fcx,
                front=-1 if fcx < tcx else 1, top=min(p[1] for p in turban))


def jester(im, turban_idx=(O_TURBAN, O_TURBAN_D), shade_idx=None):
    w, h = im.size
    px = im.load()
    info = head_info(px, w, h, turban_idx, shade_idx)
    turban = info["turban"] if info else set()

    # 1) los colores de siempre, a los índices nuevos
    remap = {O_TIGHTS_D2: TIGHTS_D, O_SHOE_HI: SHOE, O_SASH: GOLD, O_TURBAN_D: TUNIC_D}
    body = {}
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if (x, y) in turban:
                body[(x, y)] = None  # se redibuja como gorro
            else:
                body[(x, y)] = remap.get(v, v)

    # 2) rombos de arlequín en el jubón, anclados al cinturón (así no "nadan" entre frames)
    sash = [(x, y) for y in range(h) for x in range(w) if px[x, y] == O_SASH and (x, y) not in turban]
    if sash:
        ax = round(sum(p[0] for p in sash) / len(sash))
        ay = round(sum(p[1] for p in sash) / len(sash))
    else:
        ax, ay = w // 2, h
    for (x, y), v in body.items():
        if v in (TUNIC, TUNIC_HI, TUNIC_D):
            u = (x - ax + y - ay) // CELL
            t = (x - ax - y + ay) // CELL
            if (u + t) % 2 == 0:
                body[(x, y)] = MOTLEY_D if v == TUNIC_D else MOTLEY

    # 3) zapatos puntiagudos: la punta se enrosca hacia arriba, con un cascabel
    front = info["front"] if info and info.get("face") else -1
    for comp in components(_Getter(body), w, h, {SHOE}):
        if len(comp) < 3:
            continue
        yb = max(p[1] for p in comp)
        bottom = [p for p in comp if p[1] >= yb - 1]
        tip = (min if front < 0 else max)(bottom, key=lambda p: p[0])
        cx, cy = tip[0] + front, tip[1] - 1
        if 0 <= cx < w and 0 <= cy < h and not body.get((cx, cy)):
            body[(cx, cy)] = SHOE
            if 0 <= cy - 1 and not body.get((cx, cy - 1)):
                body[(cx, cy - 1)] = GOLD

    # imagen de salida, con lugar arriba para las puntas del gorro
    PAD = 7 if info else 0
    out = Image.new("P", (w, h + PAD), 0)
    out.putpalette(im.getpalette())
    o = out.load()
    for (x, y), v in body.items():
        if v:
            o[x, y + PAD] = v
    if not info:
        return out

    def put(x, y, c, over=True):
        y += PAD
        if 0 <= x < w and 0 <= y < h + PAD and (over or o[x, y] == T):
            o[x, y] = c

    # 4) gorro: el turbante se vuelve un gorro de dos colores, adelante rojo y atrás del
    # color de los rombos, con una franja dorada abajo
    tur = sorted(turban)
    ty1 = max(p[1] for p in tur)
    tcx = info["tcx"]
    face = info.get("face")
    front = info.get("front", -1)
    for x, y in tur:
        side_front = (x - tcx) * front >= 0
        c = TUNIC if side_front else MOTLEY
        if y == ty1 and face:
            c = GOLD
        put(x, y, c)
    if not face:
        return out  # de espaldas o caído: el gorro sin puntas

    top = info["top"]
    top_row = [p for p in tur if p[1] <= top + 1]
    x_front = (min if front < 0 else max)(p[0] for p in top_row)
    x_back = (max if front < 0 else min)(p[0] for p in top_row)
    b = -front
    # punta de atrás: sube hacia atrás y cae, con cascabel
    for dx, dy in ((0, -1), (1, -1), (1, -2), (2, -2), (2, -3), (3, -3), (4, -3), (4, -2), (5, -2), (5, -1)):
        put(x_back + b * dx, top + dy, MOTLEY)
    for dx, dy in ((0, -1), (1, -1), (2, -2), (3, -2)):  # grosor en la base
        put(x_back + b * dx, top + dy + 1, MOTLEY, over=False)
    for dx, dy in ((5, 0), (6, 0), (5, 1), (6, 1)):
        put(x_back + b * dx, top + dy, GOLD)
    # punta de adelante: más alta, cae hacia adelante, con cascabel
    for dx, dy in ((0, -1), (0, -2), (1, -3), (1, -4), (2, -4), (2, -5), (3, -5), (4, -5), (4, -4), (5, -4), (5, -3)):
        put(x_front + front * dx, top + dy, TUNIC)
    for dx, dy in ((1, -1), (1, -2), (2, -3), (3, -4)):
        put(x_front + front * dx, top + dy, TUNIC, over=False)
    for dx, dy in ((5, -2), (6, -2), (5, -1), (6, -1)):
        put(x_front + front * dx, top + dy, GOLD)

    # 5) gorguera: dos filas en zigzag abajo de la cara
    fpad = [(x, y + PAD) for x, y in face]
    neck_y = max(p[1] for p in fpad) + 1
    ncx = sum(p[0] for p in fpad) / len(fpad)
    for k, y in enumerate((neck_y - 1, neck_y, neck_y + 1)):
        if y >= h + PAD:
            continue
        for x in range(w):
            if abs(x - ncx) > (1.5 if k == 0 else 2.5) or o[x, y] in (T, GOLD):
                continue
            if k == 0 and o[x, y] in SKIN:
                continue  # la fila de arriba sólo tapa el cuello, no la cara
            if k == 2:
                if x % 2 == 0:
                    o[x, y] = RUFF  # el borde de abajo, en picos
            elif k == 1 and abs(x - ncx) > 1.5:
                o[x, y] = RUFF_D  # las puntas del cuello, en sombra
            else:
                o[x, y] = RUFF
    return out


class _Getter:
    """Adaptador para usar components() sobre un dict {(x, y): índice}."""
    def __init__(self, d):
        self.d = d

    def __getitem__(self, key):
        return self.d.get(key) or 0


def convert(folder, png_palette=None, shade_idx=None):
    src = os.path.join(ROOT, "data", folder)
    dst = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", folder)
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(src, "res*.png"))):
        im = jester(Image.open(f), shade_idx=shade_idx)
        if png_palette:
            pal = (im.getpalette() + [0] * 768)[:768]
            for k, rgb in enumerate(png_palette):
                if rgb is not None:
                    pal[k * 3:k * 3 + 3] = rgb
            im.putpalette(pal)
        im.save(os.path.join(dst, os.path.basename(f)), transparency=0)
        n += 1
    print(f"{n} bufones -> {dst}")


def main():
    convert("GUARD")
    convert("FAT", palette(MOTLEYS[1]), shade_idx=O_ROBE_HI)
    data = bytearray(open(SRC_PAL, "rb").read())
    for g in range(len(data) // 48):
        for k, rgb in enumerate(palette(MOTLEYS[g % len(MOTLEYS)])):
            if rgb is None:
                continue
            for c in range(3):
                data[g * 48 + k * 3 + c] = rgb[c] >> 2  # VGA de 6 bits
    os.makedirs(os.path.dirname(DST_PAL), exist_ok=True)
    open(DST_PAL, "wb").write(data)
    print(f"{len(data) // 48} paletas de bufón -> {DST_PAL}")


if __name__ == "__main__":
    main()
