#!/usr/bin/env python3
"""Imagen promocional (promo.png, 1280x720): la que se ve al compartir el link y
en la pantalla de carga de la web.

El fondo y el logo del título, Macri con sus globos, Cristina atacando con el
bastón y Máximo esperando, todo con los sprites del juego (correr antes
make_kid.py, make_baton.py, make_maximo.py, make_macri.py y make_title.py).
"""
import os
import re
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MOD = os.path.join(ROOT, "mods", "CristinaOfPersia")
DATA = os.path.join(MOD, "data")
OUT = os.path.join(MOD, "promo.png")
SCALE = 4
W, H = 320, 180
STRIKE_FRAME = 154   # Cristina a fondo, con el bastón adelante


def sprite(folder, res, flip=False):
    path = os.path.join(DATA, folder, f"res{res}.png")
    if not os.path.exists(path):
        path = os.path.join(ROOT, "data", folder, f"res{res}.png")
    im = Image.open(path).convert("RGBA")
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


def tables():
    """frame_table_kid y sword_tbl, leídas de src/seg006.c."""
    src = open(os.path.join(ROOT, "src", "seg006.c")).read()

    def table(start):
        body = src[src.index(start):]
        body = body[:body.index("};")]
        rows = re.findall(r"\{([^}]*)\}", body)
        return [[int(v, 0) for v in re.findall(r"0x[0-9A-Fa-f]+|-?\d+", r.replace("|", " "))] for r in rows]

    frames = table("const frame_type frame_table_kid[] = {")
    swords = table("const sword_table_type sword_tbl[] = {")
    return frames, swords


CHAR = 2  # los personajes van al doble de escala que el fondo, para que se luzcan


def put(canvas, im, x, bottom, scale=1):
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    canvas.alpha_composite(im, (x, bottom - im.height + 1))


def cristina_strike(canvas, x, bottom):
    """Cristina y su bastón, ubicados como los ubica el juego (mirando a la izquierda)."""
    frames, swords = tables()
    frame = frames[STRIKE_FRAME]
    image, sword = frame[0], frame[2]  # {imagen, 0x00|espada, dx, dy, flags}
    put(canvas, sprite("KID", 401 + image), x, bottom, CHAR)
    sid, sx, sy = swords[sword]
    baton = sprite("PRINCE", 735 + sid)  # la segunda mitad: el arma propia de Cristina
    put(canvas, baton, x - sx * CHAR, bottom + sy * CHAR, CHAR)


def main():
    title = Image.open(os.path.join(ROOT, "data", "TITLE", "res51.png")).convert("RGBA")
    canvas = title.crop((0, 10, W, 10 + H))
    logo = sprite("TITLE", 54)
    put(canvas, logo, (W - logo.width) // 2, 4 + logo.height)

    floor = H - 7
    # Macri, mirando hacia Cristina, con globos amarillos
    for bx, by in ((4, 124), (20, 98), (92, 118), (108, 94)):
        put(canvas, sprite("PV", 963), bx, by, CHAR)
    put(canvas, sprite("PV", 851, flip=True), 44, floor, CHAR)
    cristina_strike(canvas, 178, floor)
    put(canvas, sprite("PV", 801), 276, floor, CHAR)

    out = canvas.resize((W * SCALE, H * SCALE), Image.NEAREST).convert("RGB")
    out.save(OUT, optimize=True)
    print(f"promo -> {OUT}")


if __name__ == "__main__":
    main()
