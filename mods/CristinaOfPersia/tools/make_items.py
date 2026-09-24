#!/usr/bin/env python3
"""Objetos del mundo (data/PRINCE, grupo 150):

- res160 / res161: la espada tirada en el piso (y su destello) -> bastón presidencial
- res162 / res164: poción chica (calabozo / palacio) -> mate con bombilla
- res163 / res165: poción grande (calabozo / palacio) -> termo verde
- res174: cartel del FMI clavado entre los pinches (imagen nueva; el juego la dibuja
  si res150.pal declara 24 imágenes, ver draw_tile_anim en src/seg008.c)
Las burbujas de colores que salen de las pociones las sigue dibujando el juego:
ahora parecen el vapor del mate.

Arte hecho a mano, píxel por píxel, en el mismo tamaño que el original.
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "PRINCE")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "PRINCE")

PALETTE = {
    ".": (0, 0, 0),          # 0 transparente
    "1": (214, 218, 228),    # plata
    "2": (132, 136, 150),    # plata oscura
    "3": (88, 50, 26),       # calabaza sombra
    "4": (138, 84, 40),      # calabaza
    "5": (186, 126, 64),     # calabaza brillo
    "6": (98, 142, 40),      # yerba
    "7": (150, 190, 64),     # yerba clara
    "g": (38, 112, 62),      # termo verde
    "G": (86, 164, 96),      # termo brillo
    "s": (22, 70, 40),       # termo sombra
    "k": (30, 22, 22),       # caña de ébano
    "b": (104, 76, 60),      # brillo de la caña
    "o": (246, 206, 72),     # oro
    "O": (176, 124, 28),     # oro oscuro
    "w": (252, 252, 252),    # destello
    "B": (0, 84, 160),       # azul FMI
    "W": (244, 244, 244),    # cartel
    "d": (60, 44, 30),       # borde / poste
}
KEYS = list(PALETTE)

MATE = [
    "......1...",
    "......1...",
    ".....1....",
    "..7761767.",
    ".11111111.",
    ".45554443.",
    "3455444443",
    "3455444443",
    "3445444433",
    ".34444433.",
    "..333333..",
]

TERMO = [
    "...2222...",
    "..211112..",
    "..222222..",
    "..sGggss..",
    "..sGggss22",
    "..sGggss.2",
    "..sGggss.2",
    "..sGggss.2",
    "..sGggss.2",
    "..sGggss22",
    "..sGggss..",
    "..sGggss..",
    "..211112..",
    "..sGggss..",
    "..ssssss..",
]

BATON = [
    "................................",
    "................................",
    "................................",
    "........................ooo.....",
    ".......................ooooo....",
    "1bbbbbbbbbbbbbbbbbbbbb11oooooO..",
    "1kkkkkkkkkkkkkkkkkkkkk22oooooO..",
    "1kkkkkkkkkkkkkkkkkkkkk22OoooO...",
    "........................O.O.....",
    ".......................oo.oo....",
]

FMI_SIGN = [
    "ddddddddddddddddddd",
    "dWWWWWWWWWWWWWWWWWd",
    "dWBBBWBWWWBWBBBWWWd",
    "dWBWWWBBWBBWWBWWWWd",
    "dWBBWWBWBWBWWBWWWWd",
    "dWBWWWBWWWBWWBWWWWd",
    "dWBWWWBWWWBWBBBWWWd",
    "dWWWWWWWWWWWWWWWWWd",
    "ddddddddddddddddddd",
    ".........dd........",
    ".........dd........",
    ".........dd........",
    ".........dd........",
    ".........dd........",
    ".........dd........",
    ".........dd........",
]


def build(rows):
    h, w = len(rows), len(rows[0])
    im = Image.new("P", (w, h), 0)
    pal = []
    for k in KEYS:
        pal += PALETTE[k]
    im.putpalette(pal + [0] * (768 - len(pal)))
    px = im.load()
    for y, row in enumerate(rows):
        assert len(row) == w, (y, row)
        for x, ch in enumerate(row):
            px[x, y] = KEYS.index(ch)
    im.info["transparency"] = 0
    return im


def save(im, res):
    ref_path = os.path.join(SRC, f"res{res}.png")
    if os.path.exists(ref_path):
        ref = Image.open(ref_path)
        assert im.size == ref.size, (res, im.size, ref.size)
    im.save(os.path.join(DST, f"res{res}.png"), transparency=0)


def main():
    os.makedirs(DST, exist_ok=True)
    baton = build(BATON)
    save(baton, 160)
    # destello: el mismo bastón con la estrella blanca del original encima
    spark = baton.copy()
    ref = Image.open(os.path.join(SRC, "res161.png"))
    rp, sp = ref.load(), spark.load()
    white = KEYS.index("w")
    for y in range(ref.size[1]):
        for x in range(ref.size[0]):
            if ref.getpalette()[rp[x, y] * 3:rp[x, y] * 3 + 3] == [252, 252, 252] and rp[x, y]:
                sp[x, y] = white
    save(spark, 161)
    for res in (162, 164):
        save(build(MATE), res)
    for res in (163, 165):
        save(build(TERMO), res)
    save(build(FMI_SIGN), 174)
    pal = bytearray(open(os.path.join(SRC, "res150.pal"), "rb").read())
    pal[0] = 24  # una imagen más: el cartel
    open(os.path.join(DST, "res150.pal"), "wb").write(pal)
    print(f"objetos -> {DST}")


if __name__ == "__main__":
    main()
