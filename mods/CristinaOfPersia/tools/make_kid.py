#!/usr/bin/env python3
"""Genera los sprites de Cristina a partir de data/KID/res4xx-6xx.png.

- Ropa blanca -> traje azul marino con mangas largas (sólo cara y manos quedan en piel)
- Pelo rubio corto -> pelo castaño oscuro largo
- Cinturón dorado -> banda presidencial celeste y blanca en diagonal
- Pies descalzos -> zapatos marrón oscuro

Mantiene el tamaño exacto de cada imagen para no romper la alineación.
Uso: python3 make_kid.py   (desde cualquier carpeta)
"""
import os, glob
from collections import deque
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "KID")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "KID")

# Índices de la paleta original
T, HAIR, EYE, HAIR_D, SKIN_D, SKIN, CLOTH_EDGE, CLOTH = 0, 1, 2, 4, 5, 6, 7, 15
FOOT_A, FOOT_B = 13, 14
SASH_BLUE, SASH_WHITE = 11, 10  # 11 no se usa, 10 se usa 1 vez (duplicado de 2)
SLEEVE_D = 8  # se usa 20 veces (gris); esos píxeles pasan a CLOTH_EDGE
SKIN_ALL = (EYE, 3, SKIN_D, SKIN)
LIPS = 3  # se usaba 24 veces (piel clara); esos píxeles pasan a SKIN

NEW_COLORS = {
    HAIR: (74, 42, 26),
    HAIR_D: (40, 22, 14),
    CLOTH: (34, 42, 118),
    CLOTH_EDGE: (78, 94, 182),
    SLEEVE_D: (20, 24, 72),
    EYE: (44, 20, 24),       # ojo delineado
    LIPS: (196, 30, 58),     # labios rojos
    FOOT_A: (74, 44, 30),
    FOOT_B: (44, 26, 18),
    SASH_BLUE: (108, 172, 228),
    SASH_WHITE: (245, 245, 245),
}

HAIR_LEN = 7
SASH_ROWS = 11
PAINTABLE = {T, CLOTH, CLOTH_EDGE}


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


def lips(px, w, h, top, bottom, back):
    """Labios rojos: el píxel de piel más adelantado dos filas debajo del ojo."""
    eyes = [(x, y) for y in range(top, min(h, bottom + 2)) for x in range(w) if px[x, y] == EYE]
    if len(eyes) != 1:
        return
    ex, ey = eyes[0]
    y = ey + 2
    if y >= h:
        return
    row = [x for x in range(w) if px[x, y] in (SKIN, SKIN_D) and abs(x - ex) <= 2]
    if row:
        x = min(row) if back > 0 else max(row)
        px[x, y] = LIPS


def sleeves(px, w, h, hair_px, back, bottom):
    """Cubre los brazos con mangas: toda la piel fuera de la cabeza pasa a ser
    tela, salvo la mano (la punta del brazo más lejana al cuello)."""
    hx = [p[0] for p in hair_px]
    top = min(p[1] for p in hair_px)
    x_lo, x_hi = min(hx) - 4, max(hx) + 4
    in_head = lambda x, y: top - 2 <= y <= bottom + 2 and x_lo <= x <= x_hi
    neck = (sum(hx) / len(hx), bottom + 2)
    arms = [c for c in components(px, w, h, set(SKIN_ALL))]
    for c in arms:
        body = [p for p in c if not in_head(*p)]
        if len(body) <= 4:
            continue
        hand = max(body, key=lambda p: (p[0] - neck[0]) ** 2 + (p[1] - neck[1]) ** 2)
        for x, y in body:
            if max(abs(x - hand[0]), abs(y - hand[1])) <= 1:
                continue
            px[x, y] = SLEEVE_D if px[x, y] in (SKIN_D, EYE) else CLOTH


def transform(im):
    im = im.copy()
    w, h = im.size
    px = im.load()
    # el único uso del índice 10 pasa a su duplicado (2)
    for y in range(h):
        for x in range(w):
            if px[x, y] == SASH_WHITE:
                px[x, y] = EYE
            elif px[x, y] == SLEEVE_D:
                px[x, y] = CLOTH_EDGE
            elif px[x, y] == LIPS:
                px[x, y] = SKIN

    comps = components(px, w, h, {HAIR, HAIR_D})
    # el pelo es una mancha grande (>= 12 px); el cinturón, una tira chica
    hair = [c for c in comps if len(c) >= 12]
    belt = [c for c in comps if 3 <= len(c) < 12]
    hair_px = [p for c in hair for p in c]

    neck = None
    if hair_px:
        hx = [p[0] for p in hair_px]
        hy = [p[1] for p in hair_px]
        cx = sum(hx) / len(hx)
        top, bottom = min(hy), max(hy)
        # ¿Hacia dónde mira? La cara (piel) está del lado opuesto a la nuca.
        face = [(x, y) for y in range(top, min(h, bottom + 3)) for x in range(w)
                if px[x, y] in (SKIN, SKIN_D, EYE)]
        if face:
            fx = sum(p[0] for p in face) / len(face)
            back = 1 if fx < cx else -1
        else:
            back = 1
        # columnas de la nuca: mitad trasera del pelo + 1 columna extra de volumen
        cols = {}
        for x, y in hair_px:
            if (x - cx) * back >= -0.5:
                cols[x] = max(cols.get(x, -1), y)
        edge = max(cols, key=lambda x: x * back)
        if 0 <= edge + back < w:
            cols[edge + back] = cols[edge] - 1
        xs = sorted(cols, key=lambda x: x * back)
        for i, x in enumerate(xs):
            length = HAIR_LEN - (1 if i == len(xs) - 1 else 0)
            for dy in range(1, length + 1):
                y = cols[x] + dy
                if y >= h or px[x, y] not in PAINTABLE:
                    if y < h and px[x, y] in (HAIR, HAIR_D):
                        continue
                    break
                px[x, y] = HAIR_D if (i == len(xs) - 1 or dy == length) else HAIR
        neck = (cx - back * 1, bottom + 2)
        sleeves(px, w, h, hair_px, back, bottom)
        lips(px, w, h, top, bottom, back)

    # Banda presidencial: diagonal de un hombro a la cadera opuesta, sólo sobre la ropa
    for c in belt:
        for p in c:
            px[p] = SASH_BLUE
    if neck:
        y0 = int(neck[1])
        rows = []
        for y in range(y0, min(h, y0 + SASH_ROWS)):
            xs = [x for x in range(w) if px[x, y] in (CLOTH, CLOTH_EDGE, HAIR, HAIR_D, SASH_BLUE)
                  and abs(x - neck[0]) <= 5]
            if xs:
                rows.append((y, min(xs), max(xs)))
        if len(rows) >= 5:
            n = len(rows) - 1
            for k, (y, lo, hi) in enumerate(rows):
                t = k / n
                # de adelante (hombro) hacia atrás (cadera)
                front, rear = (lo, hi) if back > 0 else (hi, lo)
                x = round(front + (rear - front) * t)
                for dx, col in ((0, SASH_BLUE), (back, SASH_WHITE)):
                    xx = x + dx
                    if 0 <= xx < w and px[xx, y] in (CLOTH, CLOTH_EDGE):
                        px[xx, y] = col

    pal = im.getpalette()
    pal = pal + [0] * (768 - len(pal))
    for i, rgb in NEW_COLORS.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    return im


def main():
    os.makedirs(DST, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(SRC, "res*.png"))):
        im = Image.open(f)
        out = transform(im)
        out.save(os.path.join(DST, os.path.basename(f)))
        n += 1
    print(f"{n} frames -> {DST}")


if __name__ == "__main__":
    main()
