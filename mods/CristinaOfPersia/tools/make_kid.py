#!/usr/bin/env python3
"""Genera los sprites de Cristina a partir de data/KID/res4xx-6xx.png.

- Pelo rubio corto -> melena castaña larga, con volumen, flequillo y un brillo caoba
- Cara: ojos delineados y labios rojos
- Ropa blanca -> traje azul con mangas largas (sólo cara y manos quedan en piel)
- Cinturón dorado -> banda presidencial celeste, blanca y celeste en diagonal,
  con el sol de mayo dorado donde se cruza a la altura de la cadera
- Pies descalzos -> zapatos oscuros

Los colores nuevos van desde el índice 16 de la paleta de cada PNG (el juego usa
la paleta de la imagen). Mantiene el tamaño exacto de cada imagen.
Uso: python3 make_kid.py   (desde cualquier carpeta)
"""
import os, glob
from collections import deque
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "KID")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "KID")

# Índices de la paleta original
T, HAIR, EYE, LIPS, HAIR_D, SKIN_D, SKIN, CLOTH_EDGE, SLEEVE_D, CLOTH = 0, 1, 2, 3, 4, 5, 6, 7, 8, 15
FOOT_A, FOOT_B = 13, 14
DUP_EYE = 10  # se usa 1 vez: es un duplicado del ojo
SKIN_ALL = (EYE, LIPS, SKIN_D, SKIN)

# Índices nuevos (16 en adelante)
HAIR_HI, SASH_BLUE, SASH_WHITE, SUN, SUN_D, CLOTH_HI, SHOE_HI = range(16, 23)

COLORS = {
    HAIR: (108, 60, 36),       # castaño
    HAIR_D: (60, 32, 22),      # castaño oscuro
    HAIR_HI: (164, 92, 52),    # brillo caoba
    EYE: (30, 14, 18),         # ojo delineado
    LIPS: (206, 26, 56),       # labios rojos
    CLOTH: (44, 56, 142),      # traje azul
    CLOTH_EDGE: (26, 32, 92),  # sombra del traje
    CLOTH_HI: (84, 104, 196),  # brillo del traje (hombros)
    SLEEVE_D: (26, 32, 92),
    FOOT_A: (40, 26, 22),      # zapatos
    FOOT_B: (22, 14, 12),
    SHOE_HI: (96, 64, 52),
    SASH_BLUE: (116, 184, 236),
    SASH_WHITE: (248, 248, 248),
    SUN: (248, 204, 40),
    SUN_D: (196, 136, 20),
}

HAIR_LEN = 10   # cuánto baja la melena por la espalda
SASH_ROWS = 12
PAINTABLE = {T, CLOTH, CLOTH_EDGE, CLOTH_HI}


def components(px, w, h, allowed):
    seen, comps = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or px[x, y] not in allowed:
                continue
            comp, q = [], deque([(x, y)])
            seen.add((x, y))
            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and px[nx, ny] in allowed:
                            seen.add((nx, ny))
                            q.append((nx, ny))
            comps.append(comp)
    return comps


def find_eye(px, w, h, top, bottom):
    eyes = [(x, y) for y in range(top, min(h, bottom + 3)) for x in range(w) if px[x, y] == EYE]
    return eyes[0] if len(eyes) == 1 else None


def lips(px, w, h, eye, back):
    """Labios rojos: el píxel de piel más adelantado dos filas debajo del ojo."""
    ex, ey = eye
    y = ey + 2
    if y >= h:
        return
    row = [x for x in range(w) if px[x, y] in (SKIN, SKIN_D) and abs(x - ex) <= 2]
    if row:
        x = min(row) if back > 0 else max(row)
        px[x, y] = LIPS


def makeup(px, w, h, eye, back):
    """Delineado: el ojo se estira un píxel hacia la sien."""
    ex, ey = eye
    x = ex + back
    if 0 <= x < w and px[x, ey] in (SKIN, SKIN_D):
        px[x, ey] = EYE


def bangs(px, w, h, hair_px, eye):
    """Flequillo: la frente pegada al pelo pasa a ser pelo, dejando una fila de piel
    sobre el ojo para que la mirada se vea."""
    ex, ey = eye
    hair = set(hair_px)
    for y in range(max(0, ey - 3), ey - 1):
        for x in range(w):
            if px[x, y] in (SKIN, SKIN_D) and abs(x - ex) <= 3:
                near = any((x + dx, y + dy) in hair for dx in (-1, 0, 1) for dy in (-1, 0))
                if near:
                    px[x, y] = HAIR
                    hair.add((x, y))
    return list(hair)


def volume(px, w, h, hair_px, back, top, bottom):
    """Más volumen: una columna más de pelo del lado de la nuca y arriba."""
    hair = set(hair_px)
    added = []
    for x, y in hair_px:
        for nx, ny in ((x + back, y), (x, y - 1)):
            if (nx, ny) in hair or not (0 <= nx < w and 0 <= ny < h):
                continue
            if ny < top or px[nx, ny] != T or ny > bottom:
                continue
            added.append((nx, ny))
    for p in added:
        px[p] = HAIR_D
        hair.add(p)
    return list(hair)


def shine(px, hair_px, back, cx, top):
    """Brillo caoba en la coronilla."""
    for x, y in hair_px:
        b = (x - cx) * back
        if top + 1 <= y <= top + 2 and -1.5 <= b <= 0.5 and px[x, y] == HAIR:
            px[x, y] = HAIR_HI


def sleeves(px, w, h, hair_px, back, bottom):
    """Cubre los brazos con mangas: toda la piel fuera de la cabeza pasa a ser
    tela, salvo la mano (la punta del brazo más lejana al cuello)."""
    hx = [p[0] for p in hair_px]
    top = min(p[1] for p in hair_px)
    x_lo, x_hi = min(hx) - 4, max(hx) + 4
    in_head = lambda x, y: top - 2 <= y <= bottom + 2 and x_lo <= x <= x_hi
    neck = (sum(hx) / len(hx), bottom + 2)
    for c in components(px, w, h, set(SKIN_ALL)):
        body = [p for p in c if not in_head(*p)]
        if len(body) <= 4:
            continue
        hand = max(body, key=lambda p: (p[0] - neck[0]) ** 2 + (p[1] - neck[1]) ** 2)
        for x, y in body:
            if max(abs(x - hand[0]), abs(y - hand[1])) <= 1:
                continue
            px[x, y] = SLEEVE_D if px[x, y] in (SKIN_D, EYE) else CLOTH


def long_hair(px, w, h, hair_px, back, cx):
    """La melena cae por la espalda, más larga y abriéndose un poco al final."""
    cols = {}
    for x, y in hair_px:
        if (x - cx) * back >= -0.5:
            cols[x] = max(cols.get(x, -1), y)
    if not cols:
        return
    edge = max(cols, key=lambda x: x * back)
    if 0 <= edge + back < w:
        cols[edge + back] = cols[edge] - 1
    xs = sorted(cols, key=lambda x: x * back)
    for i, x in enumerate(xs):
        last = i == len(xs) - 1
        length = HAIR_LEN - (2 if last else 0) - (1 if i == 0 else 0)
        for dy in range(1, length + 1):
            y = cols[x] + dy
            if y >= h:
                break
            if px[x, y] in (HAIR, HAIR_D, HAIR_HI):
                continue
            if px[x, y] not in PAINTABLE:
                break
            px[x, y] = HAIR_D if (last or dy >= length - 1) else HAIR


def sash(px, w, h, neck, back):
    """Banda presidencial: diagonal de un hombro a la cadera opuesta, sobre la ropa."""
    y0 = int(neck[1])
    rows = []
    for y in range(y0, min(h, y0 + SASH_ROWS)):
        xs = [x for x in range(w) if px[x, y] in (CLOTH, CLOTH_EDGE, CLOTH_HI, SLEEVE_D)
              and abs(x - neck[0]) <= 5]
        if xs:
            rows.append((y, min(xs), max(xs)))
    if len(rows) < 5:
        return
    n = len(rows) - 1
    last = None
    for k, (y, lo, hi) in enumerate(rows):
        t = k / n
        front, rear = (lo, hi) if back > 0 else (hi, lo)
        x = round(front + (rear - front) * t)
        for dx, col in ((0, SASH_BLUE), (back, SASH_WHITE), (2 * back, SASH_BLUE)):
            xx = x + dx
            if 0 <= xx < w and px[xx, y] in (CLOTH, CLOTH_EDGE, CLOTH_HI, SLEEVE_D):
                px[xx, y] = col
        last = (x + back, y)
    # el sol de mayo, donde la banda llega a la cadera
    if last:
        sx, sy = last
        for dx, dy, col in ((0, 0, SUN), (0, -1, SUN), (-back, 0, SUN_D), (back, 0, SUN_D)):
            xx, yy = sx + dx, sy + dy
            if 0 <= xx < w and 0 <= yy < h and px[xx, yy] not in (T, SKIN, SKIN_D):
                px[xx, yy] = col


def tailor(px, w, h, neck, back):
    """Brillo en los hombros del saco (las dos filas debajo del cuello, del lado del frente)."""
    y0 = int(neck[1])
    for y in (y0, y0 + 1):
        if not 0 <= y < h:
            continue
        xs = [x for x in range(w) if px[x, y] == CLOTH and abs(x - neck[0]) <= 4]
        if xs:
            x = min(xs) if back > 0 else max(xs)
            px[x, y] = CLOTH_HI


def shoes(px, w, h):
    """Un brillo en la punta de cada zapato."""
    for c in components(px, w, h, {FOOT_A, FOOT_B}):
        if len(c) >= 3:
            px[min(c, key=lambda p: (p[1], p[0]))] = SHOE_HI


def transform(im):
    im = im.copy()
    w, h = im.size
    px = im.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == DUP_EYE:
                px[x, y] = EYE
            elif px[x, y] == SLEEVE_D:
                px[x, y] = CLOTH_EDGE
            elif px[x, y] == LIPS:
                px[x, y] = SKIN

    comps = components(px, w, h, {HAIR, HAIR_D})
    # el pelo es una mancha grande (>= 12 px); el cinturón, una tira chica
    hair = [c for c in comps if len(c) >= 12]
    belt = [c for c in comps if len(c) < 12]
    for c in belt:
        for p in c:
            px[p] = CLOTH
    hair_px = [p for c in hair for p in c]

    if hair_px:
        hx = [p[0] for p in hair_px]
        hy = [p[1] for p in hair_px]
        cx = sum(hx) / len(hx)
        top, bottom = min(hy), max(hy)
        face = [(x, y) for y in range(top, min(h, bottom + 3)) for x in range(w)
                if px[x, y] in (SKIN, SKIN_D, EYE)]
        back = 1
        if face:
            fx = sum(p[0] for p in face) / len(face)
            back = 1 if fx < cx else -1
        eye = find_eye(px, w, h, top, bottom)
        neck = (cx - back * 1, bottom + 2)
        sleeves(px, w, h, hair_px, back, bottom)
        if eye:
            hair_px = bangs(px, w, h, hair_px, eye)
        hair_px = volume(px, w, h, hair_px, back, top, bottom)
        shine(px, hair_px, back, cx, top)
        long_hair(px, w, h, hair_px, back, cx)
        if eye:
            lips(px, w, h, eye, back)
        tailor(px, w, h, neck, back)
        sash(px, w, h, neck, back)
    shoes(px, w, h)

    pal = im.getpalette()
    pal = (pal + [0] * 768)[:768]
    for i, rgb in COLORS.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    return im


def main():
    os.makedirs(DST, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(SRC, "res*.png"))):
        out = transform(Image.open(f))
        out.save(os.path.join(DST, os.path.basename(f)), transparency=0)
        n += 1
    print(f"{n} frames -> {DST}")


if __name__ == "__main__":
    main()
