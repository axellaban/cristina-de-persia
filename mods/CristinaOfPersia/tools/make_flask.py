#!/usr/bin/env python3
"""La petaca en la mano de Cristina (y de Bullrich) cuando toma una poción.

En el original la botella que el príncipe levanta para tomar está pintada con el
color de la ropa. Como la ropa ahora es el traje (o la campera de Bullrich), la
botella quedaba como una mancha azul (o negra). Acá esa mancha pasa a ser una petaca
plateada: en los frames de tomar (imágenes 192-206), los pedazos chicos del color de
la ropa que no tocan el cuerpo, o que quedan más arriba que el pelo, son la botella.

Correr después de make_kid.py y make_bullrich.py.
"""
import os
from PIL import Image
from make_kid import components

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "KID")
CLOTH = {7, 8, 15}
HAIR = 1
SILVER, SILVER_D = 23, 24
COLORS = {SILVER: (218, 222, 232), SILVER_D: (128, 132, 148)}
IMAGES = range(192, 207)


def flask(path):
    im = Image.open(path)
    w, h = im.size
    px = im.load()
    comps = sorted(components(px, w, h, CLOTH), key=len, reverse=True)
    # lo que está más arriba que el pelo también es la botella (cuando la mano la
    # levanta y el brazo la une al cuerpo)
    hair = [y for y in range(h) for x in range(w) if px[x, y] == HAIR]
    if hair and comps:
        top = min(hair)
        above = [p for p in comps[0] if p[1] < top]
        if 0 < len(above) <= 30:
            comps.insert(1, above)
    changed = False
    for comp in comps[1:]:  # el primero es el cuerpo
        if len(comp) > 30:
            continue
        x1 = max(p[0] for p in comp)
        y1 = max(p[1] for p in comp)
        for x, y in comp:
            px[x, y] = SILVER_D if (x == x1 or y == y1) else SILVER
        changed = True
    if changed:
        pal = (im.getpalette() + [0] * 768)[:768]
        for i, rgb in COLORS.items():
            pal[i * 3:i * 3 + 3] = rgb
        im.putpalette(pal)
        im.save(path, transparency=0)
    return changed


def main():
    n = 0
    for base in (400, 1400):
        for i in IMAGES:
            path = os.path.join(DST, f"res{base + 1 + i}.png")
            if os.path.exists(path) and flask(path):
                n += 1
    print(f"petaca en la mano: {n} imágenes -> {DST}")


if __name__ == "__main__":
    main()
