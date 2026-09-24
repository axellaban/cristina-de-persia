#!/usr/bin/env python3
"""Íconos de la web: favicon, ícono de la app (Android/Chrome) y el de iPhone.

Pixel art de 32x32: Cristina de frente, con la melena, el flequillo, los labios
rojos, el traje azul y la banda presidencial, empuñando el bastón presidencial
como una espada, delante del sol de mayo, sobre las franjas celeste y blanca. La figura se dibuja en una capa aparte y se agranda sin
suavizar; el fondo se pinta al tamaño final, así se puede dejar margen (el ícono
"maskable" de Android necesita que lo importante quede en el 80% del centro).

Uso: python3 make_icon.py   (escribe en webbuild/)
"""
import math
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "webbuild")
N = 32

C = {
    "celeste": (116, 184, 236),
    "blanco": (248, 248, 248),
    "sol": (248, 196, 32),
    "sol_d": (214, 144, 16),
    "pelo": (108, 60, 36),
    "pelo_d": (60, 32, 22),
    "pelo_hi": (164, 92, 52),
    "piel": (240, 180, 150),
    "piel_d": (206, 136, 110),
    "ojo": (30, 14, 18),
    "labios": (206, 26, 56),
    "traje": (44, 56, 142),
    "traje_d": (26, 32, 92),
    "borde": (22, 16, 26),
    "baston": (30, 22, 22),
    "baston_hi": (104, 76, 60),
    "oro": (246, 206, 72),
    "oro_d": (176, 124, 28),
    "plata": (214, 220, 230),
}


def inside_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1


def figure():
    """La figura, sobre fondo transparente (32x32)."""
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    px = im.load()

    def put(x, y, name):
        if 0 <= x < N and 0 <= y < N:
            px[x, y] = C[name] + (255,)

    # sol de mayo detrás de la cabeza: disco y 16 rayos, largos y cortos alternados
    cx, cy = 15.5, 11.5
    for y in range(N):
        for x in range(N):
            d = math.hypot(x - cx, y - cy)
            if d <= 10.6:
                put(x, y, "sol" if d <= 9.6 else "sol_d")
    for k in range(16):
        a = math.radians(k * 22.5)
        end = 15.5 if k % 2 == 0 else 13.2
        r = 10.6
        while r <= end:
            put(round(cx + r * math.cos(a)), round(cy + r * math.sin(a)), "sol")
            r += 0.4

    # melena: cae por los costados hasta los hombros
    for y in range(3, 27):
        for x in range(N):
            if inside_ellipse(x, y, 15.5, 13, 8.2, 10.5) or (19 <= y <= 26 and (7 <= x <= 10 or 21 <= x <= 24)):
                put(x, y, "pelo")
    # traje: hombros anchos
    for y in range(22, N):
        half = 8 + (y - 22) * 0.9
        for x in range(N):
            if abs(x - 15.5) <= min(half, 14):
                put(x, y, "traje")
    # sombra del traje a los costados
    for y in range(24, N):
        for x in range(N):
            if px[x, y][3] and abs(x - 15.5) >= min(8 + (y - 22) * 0.9, 14) - 1.5:
                put(x, y, "traje_d")
    # pelo sobre los hombros (adelante del traje)
    for y in range(21, 28):
        for x in (8, 9, 10, 21, 22, 23):
            if not (y >= 26 and x in (10, 21)):
                put(x, y, "pelo")
    # cuello y cara
    for y in range(18, 24):
        for x in range(14, 18):
            put(x, y, "piel_d" if y >= 21 else "piel")
    for y in range(6, 21):
        for x in range(N):
            if inside_ellipse(x, y, 15.5, 13, 4.9, 6.8):
                put(x, y, "piel")
    # sombras de la cara (mejillas y mentón)
    for x, y in ((11, 14), (11, 15), (20, 14), (20, 15), (12, 18), (19, 18), (13, 19), (18, 19)):
        put(x, y, "piel_d")
    # flequillo, con la raya al costado
    for y in range(5, 11):
        for x in range(10, 22):
            if inside_ellipse(x, y, 15.5, 13, 5.2, 7.2) and y <= 9 + (1 if x in (11, 12, 19, 20) else 0) - (1 if x in (15, 16) else 0):
                put(x, y, "pelo")
    for x, y in ((14, 4), (13, 5), (12, 6), (11, 7), (17, 5), (18, 6)):  # brillo sobre la raya
        put(x, y, "pelo_hi")
    for y in range(8, 22):  # mechones que enmarcan la cara
        put(10, y, "pelo_d")
        put(21, y, "pelo_d")
    # ojos delineados, nariz y labios rojos
    for x, y in ((12, 11), (13, 11), (18, 11), (19, 11)):  # cejas finas
        put(x, y, "pelo_d")
    for x in (12, 13, 14, 17, 18, 19):  # ojos: delineado arriba y la pupila en el medio
        put(x, 12, "ojo")
        put(x, 13, "ojo" if x in (13, 18) else "blanco")
    put(15, 15, "piel_d")
    put(16, 16, "piel_d")
    for x in (14, 15, 16, 17):
        put(x, 18, "labios")
    put(15, 17, "labios")
    put(16, 17, "labios")
    # banda presidencial: celeste, blanca y celeste, de un hombro a la cadera opuesta
    for y in range(23, N):
        t = (y - 23) / (N - 1 - 23)
        x0 = round(11 + t * 12)
        for dx, col in ((0, "celeste"), (1, "blanco"), (2, "celeste")):
            if px[x0 + dx, y][3] and px[x0 + dx, y][:3] in (C["traje"], C["traje_d"]):
                put(x0 + dx, y, col)
    # el sol de la banda
    for x, y in ((23, 29), (24, 29), (23, 30), (24, 30)):
        put(x, y, "sol")

    # el bastón presidencial en alto, como una espada: el puño cerrado a la derecha,
    # la caña de ébano subiendo en diagonal delante del sol y la contera plateada arriba
    top, bottom = (29, 0), (26, 21)
    for y in range(top[1], bottom[1] + 1):
        x = round(top[0] + (bottom[0] - top[0]) * (y - top[1]) / (bottom[1] - top[1]))
        put(x - 1, y, "baston_hi")
        put(x, y, "baston")
        put(x + 1, y, "baston")
    for x, y in ((28, 0), (29, 0), (30, 0), (28, 1), (29, 1), (30, 1)):  # contera plateada
        put(x, y, "plata")
    for x in range(25, 29):  # virola dorada, arriba de la mano
        put(x, 18, "oro")
    for x in range(24, 28):  # la mano cerrada sobre la caña, con los dedos marcados
        for y in range(20, 24):
            put(x, y, "piel_d" if y == 23 or x == 27 else "piel")
    for x in (24, 25, 26):
        put(x, 22 if x != 25 else 21, "piel_d")
    for x, y in ((23, 24), (24, 24), (25, 24), (23, 25), (24, 25), (25, 25), (24, 26)):  # el puño dorado
        put(x, y, "oro" if (x, y) in ((23, 24), (24, 24), (23, 25)) else "oro_d")
    for x, y in ((26, 25), (26, 26), (27, 27), (27, 28)):  # cordón
        put(x, y, "oro_d")
    for x, y in ((26, 29), (27, 29), (28, 29), (26, 30), (27, 30), (28, 30), (27, 31)):  # borla
        put(x, y, "oro" if y == 29 else "oro_d")

    # contorno oscuro de la figura (sin el sol), para que se lea en cualquier tamaño
    # (la caña del bastón no lleva contorno: ya es oscura y quedaría gruesa)
    body = {C[k] for k in C if k not in ("sol", "sol_d", "celeste", "blanco", "baston", "baston_hi", "plata")}
    solid = {(x, y) for y in range(N) for x in range(N) if px[x, y][3] and px[x, y][:3] in body}
    for x, y in list(solid):
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in solid and ny < N - 1:
                if px[nx, ny][3] == 0 or px[nx, ny][:3] in (C["sol"], C["sol_d"]):
                    px[nx, ny] = C["borde"] + (255,)
    return im


def background(size):
    """Franjas celeste, blanca y celeste."""
    im = Image.new("RGBA", (size, size), C["celeste"] + (255,))
    band = Image.new("RGBA", (size, size - 2 * round(size * 0.34)), C["blanco"] + (255,))
    im.paste(band, (0, round(size * 0.34)))
    return im


def icon(size, content):
    """content: qué fracción del ícono ocupa la figura (1 = todo)."""
    im = background(size)
    fig = figure()
    scale = max(1, int(size * content) // N)
    big = fig.resize((N * scale, N * scale), Image.NEAREST)
    off = ((size - big.width) // 2, size - big.height if content >= 0.99 else (size - big.height) // 2)
    im.alpha_composite(big, off)
    return im.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    icon(32, 1).save(os.path.join(OUT, "favicon-32.png"), optimize=True)
    icon(192, 1).save(os.path.join(OUT, "icon-192.png"), optimize=True)
    icon(512, 1).save(os.path.join(OUT, "icon-512.png"), optimize=True)
    icon(180, 1).save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)
    icon(512, 0.75).save(os.path.join(OUT, "icon-maskable-512.png"), optimize=True)
    icon(64, 1).save(os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print(f"íconos -> {OUT}")


if __name__ == "__main__":
    main()
