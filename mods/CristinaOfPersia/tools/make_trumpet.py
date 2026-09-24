#!/usr/bin/env python3
"""Convierte la espada de los guardias (data/PRINCE/res701-734.png) en una trompeta.

Los bufones pelean con una trompeta dorada agarrada como una espada:

- En el extremo de la mano, la boquilla plateada
- Cerca de la mano, los tres pistones (del lado de arriba) y la vuelta del tubo (abajo)
- El tubo de bronce, de 2 px, con brillo arriba
- En la punta, la campana que se abre

Las trompetas van en res769-802, la tercera tanda de imágenes de la espada: el juego
se las da a los guardias comunes y al gordo (ver add_sword_to_objtable en
src/seg006.c). Las espadas originales (res701-734) quedan para Mauricio y el
esqueleto, y el bastón de Cristina (res735-768) no cambia.

El juego apoya la imagen por abajo y por la izquierda (la da vuelta alrededor de ese
borde cuando mira a la derecha), así que sólo se agregan filas arriba; si la campana
no entra abajo, la trompeta entera sube un poco.

Correr después de make_baton.py (usa su forma de encontrar qué extremo toca la mano).
"""
import math
import os
import glob
from PIL import Image
import make_baton
from make_baton import d2, body_distance, hand_votes

ROOT = make_baton.ROOT
SRC = make_baton.SRC
DST = make_baton.DST

T, HILT, BLADE = 0, 6, 15
BRASS, BRASS_HI, BRASS_D, SILVER, SILVER_D = 15, 14, 13, 11, 12
NEW_COLORS = {
    BRASS: (228, 172, 40),
    BRASS_HI: (252, 230, 128),
    BRASS_D: (150, 96, 20),
    SILVER: (224, 228, 236),
    SILVER_D: (140, 146, 160),
}
PAD = 4  # filas extra arriba


def ends(src, sid, uses):
    """(mano, punta) del trazo de la espada, en coordenadas de la imagen original."""
    px = src.load()
    w, h = src.size
    blade = [(x, y) for y in range(h) for x in range(w) if px[x, y] == BLADE]
    hilt = [(x, y) for y in range(h) for x in range(w) if px[x, y] == HILT]
    if len(blade) < 2:
        return None
    a = max(blade, key=lambda p: d2(p, blade[0]))
    b = max(blade, key=lambda p: d2(p, a))
    if hilt:
        hc = (sum(p[0] for p in hilt) / len(hilt), sum(p[1] for p in hilt) / len(hilt))
        return (a, b) if d2(a, hc) < d2(b, hc) else (b, a)
    if sid in uses:
        da = body_distance(a, h, uses[sid])
        db = body_distance(b, h, uses[sid])
        return (a, b) if da <= db else (b, a)
    dens = lambda e: sum(1 for p in blade if d2(p, e) <= 5)
    return (a, b) if dens(a) >= dens(b) else (b, a)


def draw(w, h, hand, tip, lift):
    """Dibuja la trompeta; devuelve {(x, y): color} (y ya con el PAD y la subida)."""
    hx, hy = hand
    tx, ty = tip
    L = math.hypot(tx - hx, ty - hy)
    ux, uy = (tx - hx) / L, (ty - hy) / L
    # normal "hacia arriba" (pistones arriba, vuelta del tubo abajo)
    nx, ny = uy, -ux
    if ny > 0 or (abs(ny) < 0.2 and nx < 0):
        nx, ny = -nx, -ny
    out = {}

    def put(t, s, color, force=True):
        x = round(hx + ux * t + nx * s)
        y = round(hy + uy * t + ny * s) + PAD - lift
        if 0 <= x < w and 0 <= y < h + PAD:
            if force or (x, y) not in out:
                out[(x, y)] = color

    step = 0.25
    bell = min(6.0, max(3.0, L * 0.34))
    body_end = L - bell
    # vuelta del tubo, abajo, entre los pistones y la campana
    if L >= 12:
        t0, t1 = L * 0.22, L * 0.58
        t = t0
        while t <= t1:
            put(t, -2, BRASS_D)
            t += step
        for s in (-1, -2):
            put(t0, s, BRASS_D)
            put(t1, s, BRASS_D)
    # tubo principal con brillo arriba
    t = 0
    while t <= body_end:
        put(t, 0, BRASS)
        put(t, 1, BRASS_HI, force=False)
        t += step
    # campana
    t = body_end
    while t <= L:
        k = (t - body_end) / bell
        hw = 0.6 + 2.6 * k ** 1.6
        s = -hw
        while s <= hw + 0.01:
            put(t, s, BRASS_HI if s > hw - 0.9 else BRASS_D if s < -hw + 0.9 else BRASS)
            s += 0.25
        t += step
    # pistones: tres, arriba, cerca de la mano
    if L >= 10:
        for f in (0.26, 0.36, 0.46):
            put(L * f, 1, SILVER_D)
            put(L * f, 2, SILVER)
    # boquilla plateada en la mano
    t = 0
    while t <= 1.2:
        put(t, 0, SILVER)
        t += step
    return out


def transform(src, sid, uses):
    w, h = src.size
    im = Image.new("P", (w, h + PAD), 0)
    pal = (src.getpalette() + [0] * 768)[:768]
    for i, rgb in NEW_COLORS.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    im.info["transparency"] = 0
    e = ends(src, sid, uses)
    if e is None:
        return im
    hand, tip = e
    # si la campana se sale por abajo, la trompeta sube (hasta 3 px)
    for lift in range(0, 4):
        pts = draw(w, h, hand, tip, lift)
        full = draw(w + 20, h + 20, hand, tip, lift)  # sin recortar, para comparar
        if all(y < h + PAD for (x, y) in full) or lift == 3:
            break
    px = im.load()
    for (x, y), c in pts.items():
        px[x, y] = c
    return im


def main():
    os.makedirs(DST, exist_ok=True)
    files = [f for f in sorted(glob.glob(os.path.join(SRC, "res7*.png")))
             if 701 <= int(os.path.basename(f)[3:6]) <= 734]
    uses = hand_votes()
    n = len(files)
    for f in files:
        sid = int(os.path.basename(f)[3:6]) - 701
        transform(Image.open(f), sid, uses).save(os.path.join(DST, f"res{701 + 2 * n + sid}.png"))
    pal = bytearray(open(os.path.join(SRC, "res700.pal"), "rb").read())
    pal[0] = 3 * n
    open(os.path.join(DST, "res700.pal"), "wb").write(pal)
    print(f"{n} trompetas -> {DST} (res{701 + 2 * n}-{700 + 3 * n})")


if __name__ == "__main__":
    main()
