#!/usr/bin/env python3
"""Convierte la espada (data/PRINCE/res701-734.png) en el bastón presidencial.

El bastón argentino: caña de madera oscura, puño dorado arriba, cordón con
borlas doradas colgando del puño y contera metálica en la punta.

- Hoja -> caña de ébano, con brillo donde el trazo tiene 2 px
- Guarda en cruz -> se elimina (el bastón no tiene); queda sólo el puño dorado
- Extremo de la mano -> puño dorado (perilla)
- Del puño cuelgan el cordón y la borla, si hay lugar dentro de la imagen
- Punta -> contera plateada

Las espadas originales (res701-734) quedan para los guardias. El bastón va en
res735-768 y un res700.pal con 68 imágenes le avisa al juego (ver
add_sword_to_objtable en src/seg006.c) que Cristina y su sombra usan la
segunda mitad.

El juego ancla las imágenes por abajo, así que agregar filas arriba no desalinea.
"""
import os, re, glob
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "PRINCE")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "PRINCE")

T, HILT, BLADE = 0, 6, 15
SHINE, GOLD_D, GOLD, SILVER = 12, 13, 14, 11
NEW_COLORS = {
    BLADE: (30, 22, 22),
    SHINE: (104, 76, 60),
    GOLD: (246, 206, 72),
    GOLD_D: (176, 124, 28),
    SILVER: (214, 220, 230),
}


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def hand_votes():
    """Para cada imagen de espada, qué extremo toca la mano del príncipe.

    Lee frame_table_kid y sword_tbl de src/seg006.c, superpone cada frame del
    príncipe con su espada tal como lo hace el juego y devuelve, por id de
    espada, el punto (en coords de la espada) más cercano al cuerpo."""
    src = open(os.path.join(ROOT, "src", "seg006.c")).read()
    kt = src[src.index("frame_table_kid[] = {"):]
    kt = kt[:kt.index("};")]
    rows = re.findall(r"\{\s*(\d+),\s*0x[0-9A-F]+\|\s*(\d+),", kt)
    st = src[src.index("sword_tbl[] = {"):]
    st = st[:st.index("};")]
    tbl = [tuple(map(int, m)) for m in re.findall(r"\{\s*(\d+),\s*(-?\d+),\s*(-?\d+)\}", st)]
    uses = {}
    for img, swl in rows:
        img, s_ = int(img), int(swl) & 0x3F
        if img == 255 or not s_ or tbl[s_][0] == 255:
            continue
        sid, sx, sy = tbl[s_]
        uses.setdefault(sid, []).append((img, sx, sy))
    return uses


def body_distance(blade_pt, sword_h, uses):
    """Distancia mínima (promedio entre usos) de un punto de la espada al cuerpo."""
    total = 0
    for img, sx, sy in uses:
        kid = Image.open(os.path.join(ROOT, "data", "KID", f"res{401 + img}.png"))
        kw, kh = kid.size
        kp = kid.load()
        # mismo cálculo que el juego (mirando a la izquierda, anclado abajo):
        # espada en x = K - sx, abajo en bottom + sy
        bx = -sx + blade_pt[0]
        by = sy - sword_h + 1 + blade_pt[1] + (kh - 1)
        best = min(((bx - x) ** 2 + (by - y) ** 2 for y in range(kh) for x in range(kw) if kp[x, y]),
                   default=10 ** 6)
        total += best
    return total / len(uses)


USES = None
PAD = 2  # filas extra arriba: el juego ancla por abajo, así que no se desalinea


def transform(im, sid):
    src = im
    w, h = src.size[0], src.size[1] + PAD
    im = Image.new("P", (w, h), 0)
    im.putpalette(src.getpalette())
    im.paste(src, (0, PAD))
    im.info["transparency"] = 0
    px = im.load()
    blade = [(x, y) for y in range(h) for x in range(w) if px[x, y] == BLADE]
    hilt = [(x, y) for y in range(h) for x in range(w) if px[x, y] == HILT]
    if len(blade) < 2:
        return finish(im)

    # extremos del trazo: el par de píxeles más alejados
    a = max(blade, key=lambda p: d2(p, blade[0]))
    b = max(blade, key=lambda p: d2(p, a))
    if hilt:
        hc = (sum(p[0] for p in hilt) / len(hilt), sum(p[1] for p in hilt) / len(hilt))
        hand, tip = (a, b) if d2(a, hc) < d2(b, hc) else (b, a)
    elif sid in USES:
        # coords sin el PAD para comparar con el cuerpo
        da = body_distance((a[0], a[1] - PAD), src.size[1], USES[sid])
        db = body_distance((b[0], b[1] - PAD), src.size[1], USES[sid])
        hand, tip = (a, b) if da <= db else (b, a)
    else:
        # sin mano visible: la empuñadura es el extremo más grueso
        dens = lambda e: sum(1 for p in blade if d2(p, e) <= 5)
        hand, tip = (a, b) if dens(a) >= dens(b) else (b, a)

    # la guarda en cruz no existe en un bastón
    for p in hilt:
        px[p] = T

    # caña de 2 px: brillo arriba (o al costado si es casi vertical)
    horizontal = abs(a[0] - b[0]) >= abs(a[1] - b[1])
    bset = set(blade)
    for x, y in blade:
        n = (x, y - 1) if horizontal else (x + 1, y)
        if n in bset:
            continue
        if 0 <= n[0] < w and 0 <= n[1] < h and px[n] == T:
            px[n] = SHINE

    # puño dorado: una perilla de ~3x3 en el extremo de la mano
    hx, hy = hand
    for x in range(hx - 1, hx + 2):
        for y in range(hy - 2, hy + 1):
            if 0 <= x < w and 0 <= y < h:
                px[x, y] = GOLD if (x, y) != (hx - 1, hy) and (x, y) != (hx + 1, hy) else GOLD_D
    # cordón y borla colgando del puño
    for dx in (0, 1, -1, 2, -2):
        x = hx + dx
        free = 0
        while 0 <= x < w and hy + 1 + free < h and free < 3 and px[x, hy + 1 + free] == T:
            free += 1
        if free >= 2:
            for k in range(free):
                px[x, hy + 1 + k] = GOLD_D if k < free - 1 else GOLD
            break

    # contera plateada
    for p in sorted(blade, key=lambda p: d2(p, tip))[:2]:
        px[p] = SILVER
    return finish(im)


def finish(im):
    pal = im.getpalette()
    pal = pal + [0] * (768 - len(pal))
    for i, rgb in NEW_COLORS.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    return im


def main():
    os.makedirs(DST, exist_ok=True)
    files = [f for f in sorted(glob.glob(os.path.join(SRC, "res7*.png")))
             if 701 <= int(os.path.basename(f)[3:6]) <= 734]
    global USES
    USES = hand_votes()
    n = len(files)
    for f in files:
        sid = int(os.path.basename(f)[3:6]) - 701
        transform(Image.open(f), sid).save(os.path.join(DST, f"res{701 + n + sid}.png"))
        stale = os.path.join(DST, os.path.basename(f))
        if os.path.exists(stale):
            os.remove(stale)  # versiones viejas del mod que pisaban la espada
    # misma paleta que el original, con el doble de imágenes
    pal = bytearray(open(os.path.join(SRC, "res700.pal"), "rb").read())
    pal[0] = 2 * n
    open(os.path.join(DST, "res700.pal"), "wb").write(pal)
    print(f"{n} frames -> {DST} (res{701 + n}-{700 + 2 * n})")


if __name__ == "__main__":
    main()
