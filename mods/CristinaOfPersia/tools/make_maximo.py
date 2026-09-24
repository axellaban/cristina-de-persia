#!/usr/bin/env python3
"""Convierte a la princesa (data/PV/res801-817 y res901-930) en Máximo Kirchner.

- Pelo largo -> pelo oscuro corto; lo que caía por la espalda pasa a ser la espalda de la camiseta
- Cara: barba tupida en mandíbula, mentón y cuello (la nariz queda a la vista)
- Corpiño blanco -> camiseta de Racing, rayas verticales celestes y blancas
- Pollera fucsia -> jean: dos piernas desde la cadera hasta cada pie
- Pies descalzos -> zapatillas blancas
- En el abrazo final (911-916) el príncipe pasa a ser Cristina (pelo castaño largo, traje azul)

Mantiene el tamaño exacto de cada imagen.
"""
import os
from PIL import Image
from make_kid import components

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "PV")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "PV")

T = 0
HAIR, HAIR_D, HAIR_X = 4, 10, 14
SKIN_D, SKIN, SKIN_L = 5, 6, 8
BODICE, SKIRT, SKIRT_EDGE = 15, 9, 11
STRIPE = 14  # sólo se usaba en 1 píxel (el ojo)
SKIN_ALL = {SKIN_D, SKIN, SKIN_L}
# índices del príncipe en el abrazo final
KID_HAIR, KID_HAIR_D, KID_CLOTH, KID_CLOTH_D, KID_FOOT = 1, 7, 3, 12, 13
EYE = 12     # en el abrazo, la sombra del traje del príncipe (12) se funde con 3
BEARD = 13   # marrón muy oscuro, igual que los zapatos de Cristina en el abrazo

NEW_COLORS = {
    HAIR: (46, 34, 28),
    HAIR_D: (24, 18, 14),
    BODICE: (112, 178, 232),   # celeste Racing
    STRIPE: (246, 246, 246),
    SKIRT: (58, 84, 142),      # jean
    SKIRT_EDGE: (40, 58, 104),
    EYE: (34, 22, 18),
    BEARD: (74, 52, 38),
}
HUG_COLORS = {  # los mismos que Cristina en make_kid.py
    KID_HAIR: (108, 60, 36),
    KID_CLOTH: (44, 56, 142),
}
HUG = range(911, 917)
HEAD_ROWS = 7
HAIR_ROWS = 4
BACK_HAIR = 3
HIP_ROWS = 4   # filas del jean que quedan enteras (la cadera)
FOREARM = 3    # lo que queda de brazo sin manga
LEG_W = 3      # ancho de cada pierna


def cristina_hair(px, w, h):
    """En el abrazo el príncipe es Cristina: le alargamos el pelo por la espalda."""
    comps = components(px, w, h, {KID_HAIR})
    if not comps:
        return
    hair = max(comps, key=len)
    cx = sum(p[0] for p in hair) / len(hair)
    cols = {}
    for x, y in hair:
        if x >= cx - 0.5:  # mira a la izquierda (hacia Máximo): la nuca queda a la derecha
            cols[x] = max(cols.get(x, -1), y)
    for x, yb in cols.items():
        for dy in range(1, 7):
            y = yb + dy
            if y >= h or px[x, y] not in (T, KID_CLOTH):
                break
            px[x, y] = KID_HAIR


def beard(px, w, h, eye, front):
    """Barba tupida desde debajo de la nariz (con bigote); a la altura de la nariz
    sólo la patilla, así las mejillas y la nariz quedan a la vista."""
    ex, ey = eye
    for y in (ey + 1, ey + 2, ey + 3):
        if y >= h:
            continue
        row = [x for x in range(w) if px[x, y] in SKIN_ALL and abs(x - ex) <= 3]
        if not row:
            continue
        for x in row:
            if y == ey + 1 and (x - ex) * front >= -1:
                continue  # mejilla y nariz
            px[x, y] = BEARD


def jersey(px, w, h, head_bottom, waist, hx, keep_x=None):
    """El vestido no tenía breteles: hombros, pecho y espalda pasan a ser camiseta,
    con manga corta (el antebrazo y la mano quedan en piel)."""
    neck = (hx, head_bottom)
    for c in components(px, w, h, SKIN_ALL):
        body = [p for p in c if head_bottom < p[1] < waist and (keep_x is None or keep_x(p[0]))]
        if len(body) <= 2:
            continue
        hand = max(body, key=lambda p: (p[0] - neck[0]) ** 2 + (p[1] - neck[1]) ** 2)
        for x, y in body:
            if max(abs(x - hand[0]), abs(y - hand[1])) <= FOREARM:
                continue
            px[x, y] = BODICE


def curls(px, hair):
    """Pelo enrulado: puntitos más oscuros."""
    for x, y in hair:
        if px[x, y] == HAIR and (x + 2 * y) % 4 == 0:
            px[x, y] = HAIR_D


def transform(im, hug):
    im = im.copy()
    w, h = im.size
    px = im.load()
    eye = None
    for y in range(h):
        for x in range(w):
            if px[x, y] == HAIR_X:
                eye = (x, y)  # el único píxel de índice 14 es el ojo
                px[x, y] = EYE
            elif px[x, y] == KID_HAIR_D:
                px[x, y] = KID_HAIR
            elif px[x, y] == KID_CLOTH_D:
                px[x, y] = KID_CLOTH
    if hug:
        cristina_hair(px, w, h)

    comps = components(px, w, h, {HAIR, HAIR_D})
    if not comps:
        return finish(im, hug)
    hair = max(comps, key=len)
    top = min(p[1] for p in hair)
    head_bottom = top + HEAD_ROWS
    face = [(x, y) for y in range(top, min(h, head_bottom + 1)) for x in range(w)
            if px[x, y] in SKIN_ALL]
    hx = sum(p[0] for p in hair) / len(hair)
    if face:
        fx = sum(p[0] for p in face) / len(face)
        back = -1 if fx > hx else 1
        face_back = min(p[0] for p in face) if back < 0 else max(p[0] for p in face)
    else:
        back, face_back = -1, round(hx)
    has_eye = eye is not None and top <= eye[1] <= head_bottom

    # 1) pelo corto. Lo que caía por la espalda es la espalda de la camiseta;
    #    lo que sobra en la cabeza se recorta y queda el cuello, con barba
    cut = eye[1] + 1 if has_eye else top + HAIR_ROWS
    for x, y in hair:
        behind = (x - face_back) * back
        if y > head_bottom:
            px[x, y] = BODICE
        elif behind > BACK_HAIR:
            px[x, y] = T
        elif y > cut:
            px[x, y] = BEARD if behind <= 2 else T
    for c in comps:
        if c is not hair:
            for p in c:
                if p[1] > head_bottom:
                    px[p] = BODICE

    # 2) barba y rulos
    if has_eye:
        beard(px, w, h, eye, -back)
    curls(px, [p for p in hair if px[p] in (HAIR, HAIR_D)])

    # 3) de pollera a pantalón: dos piernas desde la cadera hasta cada pie;
    #    el resto de la pollera se borra. Los pies pasan a ser zapatillas blancas
    skirt_rows = [y for y in range(h) for x in range(w) if px[x, y] in (SKIRT, SKIRT_EDGE)]
    if skirt_rows and not hug and h > w:  # sólo de pie (acostado o de rodillas queda como está)
        s_top, s_bot = min(skirt_rows), max(skirt_rows)
        # la camiseta termina recta a la altura de la cadera (el corpiño bajaba en diagonal)
        for y in range(s_top + 2, h):
            for x in range(w):
                if px[x, y] in (BODICE, SKIRT_EDGE):
                    px[x, y] = SKIRT
        feet = [c for c in components(px, w, h, SKIN_ALL) if max(p[1] for p in c) >= s_bot - 1
                and min(p[1] for p in c) >= s_top + 3]
        hip_y = s_top + HIP_ROWS
        hip_xs = [x for x in range(w) if px[x, hip_y] in (SKIRT, SKIRT_EDGE)] if hip_y < h else []
        if feet and hip_xs:
            hip_x = (min(hip_xs) + max(hip_xs)) / 2
            legs = []
            for c in feet:
                fx = sum(p[0] for p in c) / len(c)
                fy = min(p[1] for p in c)
                legs.append((fx, fy))
            half = LEG_W / 2 if len(legs) > 1 else LEG_W
            # cada pierna arranca de su lado de la cadera
            legs.sort()
            starts = [hip_x - 1.5, hip_x + 1.5] if len(legs) > 1 else [hip_x]
            for y in range(hip_y, h):
                keep = set()
                for (fx, fy), sx in zip(legs, starts):
                    t = min(1, (y - hip_y) / max(1, fy - hip_y))
                    cx = sx + (fx - sx) * t
                    keep.update(x for x in range(w) if abs(x - cx) <= half)
                for x in range(w):
                    if px[x, y] in (SKIRT, SKIRT_EDGE) and x not in keep:
                        px[x, y] = T
                    elif x in keep and px[x, y] == T and y < max(fy for _, fy in legs):
                        px[x, y] = SKIRT  # pierna que asomaba fuera de la pollera
            for c in feet:
                for p in c:
                    px[p] = STRIPE

    # 4) camiseta con mangas cortas (en el abrazo, sólo del lado de Máximo)
    skirt_now = [y for y in range(h) for x in range(w) if px[x, y] in (SKIRT, SKIRT_EDGE)]
    waist = (min(skirt_now) + 2) if skirt_now else head_bottom + 12
    keep_x = None
    if hug:
        keep_x = (lambda x: (x - hx) * back >= -2)  # Cristina queda del otro lado
    jersey(px, w, h, head_bottom, waist, hx, keep_x)

    # 5) camiseta de Racing: rayas verticales
    for y in range(h):
        for x in range(w):
            if px[x, y] == BODICE and x % 2:
                px[x, y] = STRIPE
    return finish(im, hug)


def finish(im, hug):
    pal = im.getpalette()
    pal = pal + [0] * (768 - len(pal))
    colors = dict(NEW_COLORS)
    if hug:
        colors.update(HUG_COLORS)
    for i, rgb in colors.items():
        pal[i * 3:i * 3 + 3] = rgb
    im.putpalette(pal)
    return im


def main():
    os.makedirs(DST, exist_ok=True)
    ids = list(range(801, 818)) + [i for i in range(901, 931) if i != 902]
    for i in ids:
        name = f"res{i}.png"
        transform(Image.open(os.path.join(SRC, name)), i in HUG).save(os.path.join(DST, name))
    print(f"{len(ids)} frames -> {DST}")


if __name__ == "__main__":
    main()
