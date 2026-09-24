#!/usr/bin/env python3
"""Los guardias pasan a ser Granaderos (la guardia presidencial).

Los sprites de los guardias vienen en escala de grises y el juego los pinta
con una de 7 paletas según el nivel (data/PRINCE/res10.bin, 16 colores VGA de
6 bits cada una). Acá se reescriben esas paletas:

- casaca azul oscuro, pantalón blanco, correaje blanco, morrión negro, botas negras
- el color del penacho/vivos cambia con la paleta, para que se sigan
  distinguiendo los guardias más fuertes
"""
import os

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


def main():
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
