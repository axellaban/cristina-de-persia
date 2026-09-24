#!/usr/bin/env python3
"""Pinches -> palas (data/VDUNGEON y data/VPALACE, grupo 200).

Los pinches se dibujan en tres capas, cada una con 5 etapas de la animación:
- res328-332: detrás del príncipe
- res334-338: la parte que asoma en la baldosa de al lado
- res339-343: delante del príncipe (repite algunos pinches de res328-332, alineados)

Cada pinche del original es un trazo fino; en su lugar se dibuja una pala de punta
con la hoja hacia arriba y el mango de madera hacia el piso, con la misma base,
altura e inclinación, así las capas siguen encajando y la animación de salida
se ve igual (en las primeras etapas sólo asoman las puntas).
En la capa de atrás se agregan palas más bajas entre las otras: muchas palas.
El cartel del FMI (make_items.py) sigue clavado detrás.
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FOLDERS = ("VDUNGEON", "VPALACE")
BACK = range(328, 333)
SIDE = range(334, 339)
FRONT = range(339, 344)

# Los colores van desde el índice 16: si un nivel usa colores alternativos,
# el juego reemplaza los primeros 16 de la paleta de estas imágenes.
COLORS = {
    "hi": (226, 230, 238),     # filo / brillo de la hoja
    "mid": (160, 166, 180),    # hoja
    "dark": (92, 98, 112),     # sombra de la hoja y cubo
    "wood": (164, 108, 52),    # mango
    "wood2": (112, 70, 34),    # mango sombra
}
FIRST = 16
INDEX = {name: FIRST + i for i, name in enumerate(COLORS)}

# ancho de la hoja por fila, desde la punta; después, el cubo y el mango
BIG_BLADE = [1, 3, 5, 5, 5, 5, 5]
SMALL_BLADE = [1, 3, 3, 3, 3]
SOCKET = 1


def strokes(im):
    """Cada pinche del original: (x arriba, y arriba, x abajo, y abajo)."""
    w, h = im.size
    px = im.load()
    tr = im.info.get("transparency", 0)
    seen, out = set(), []
    for y in range(h):
        for x in range(w):
            if px[x, y] == tr or (x, y) in seen:
                continue
            stack, pts = [(x, y)], []
            seen.add((x, y))
            while stack:
                a, b = stack.pop()
                pts.append((a, b))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        n = (a + dx, b + dy)
                        if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and px[n] != tr:
                            seen.add(n)
                            stack.append(n)
            top = min(p[1] for p in pts)
            bot = max(p[1] for p in pts)
            tx = sum(p[0] for p in pts if p[1] == top) / sum(1 for p in pts if p[1] == top)
            bx = sum(p[0] for p in pts if p[1] == bot) / sum(1 for p in pts if p[1] == bot)
            out.append((tx, top, bx, bot))
    return sorted(out, key=lambda s: s[2])


def full_heights(paths):
    """Alto final de cada pala (por la x de su base), mirando todas las etapas.
    Así, mientras sale, se ve la punta de la misma pala que después queda afuera."""
    full = {}
    for path in paths:
        for tx, top, bx, bot in strokes(Image.open(path)):
            key = round(bx)
            full[key] = max(full.get(key, 0), bot - top)
    return full


def full_height(full, bx):
    return max((h for key, h in full.items() if abs(key - bx) <= 1), default=0)


def extras(main, full):
    """Palas finitas y más bajas entre las palas que están separadas."""
    out = []
    for a, b in zip(main, main[1:]):
        if b[2] - a[2] < 6:
            continue
        bot = round((a[3] + b[3]) / 2)
        grown = min((a[3] - a[1]) / max(full_height(full, a[2]), 1), (b[3] - b[1]) / max(full_height(full, b[2]), 1))
        height = round(min(full_height(full, a[2]), full_height(full, b[2])) * 0.6 * grown)
        if height < 2:
            continue
        bx = (a[2] + b[2]) / 2
        tx = bx + ((a[0] - a[2]) + (b[0] - b[2])) / 4
        out.append((tx, bot - height, bx, bot, "small"))
    return out


def draw_shovel(px, size, stroke, blade):
    tx, top, bx, bot = stroke[:4]
    w, h = size
    length = bot - top
    for t in range(length + 1):
        y = top + t
        cx = round(tx + (bx - tx) * (t / length if length else 0))
        if t < len(blade):
            half = blade[t] // 2
            for dx in range(-half, half + 1):
                if dx == -half and half > 0 or t == 0:
                    color = "hi"
                elif dx == half and half > 0:
                    color = "dark"
                else:
                    color = "mid"
                if 0 <= cx + dx < w and 0 <= y < h:
                    px[cx + dx, y] = INDEX[color]
        elif t < len(blade) + SOCKET:
            if 0 <= cx < w:
                px[cx, y] = INDEX["dark"]
        else:
            if 0 <= cx < w:
                px[cx, y] = INDEX["wood2" if t % 5 == 4 else "wood"]


def make(src_path, full, with_extras):
    src = Image.open(src_path)
    main = strokes(src)
    shovels = (extras(main, full) if with_extras else []) + main
    right = max(max(s[0], s[2]) for s in shovels)
    w = max(src.width, int(right) + max(BIG_BLADE) // 2 + 2)
    h = src.height
    im = Image.new("P", (w, h), 0)
    pal = [0, 0, 0] * FIRST
    for c in COLORS.values():
        pal += c
    im.putpalette(pal + [0] * (768 - len(pal)))
    px = im.load()
    for s in shovels:
        big = len(s) == 4 and full_height(full, s[2]) >= 16
        draw_shovel(px, (w, h), s, BIG_BLADE if big else SMALL_BLADE)
    return im


def main():
    for folder in FOLDERS:
        src_dir = os.path.join(ROOT, "data", folder)
        dst_dir = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", folder)
        os.makedirs(dst_dir, exist_ok=True)
        for layer in (BACK, SIDE, FRONT):
            paths = {res: os.path.join(src_dir, f"res{res}.png") for res in layer}
            full = full_heights(paths.values())
            for res, path in paths.items():
                im = make(path, full, with_extras=layer is BACK)
                im.save(os.path.join(dst_dir, f"res{res}.png"), transparency=0)
        print(f"palas -> {dst_dir}")


if __name__ == "__main__":
    main()
