#!/usr/bin/env python3
"""Mete la letra del juego (data/font) en webbuild/index.html, para la pantalla de
inicio de la web: la misma letra y el mismo armado que la pantalla de inicio de
SDLPoP (show_splash en src/seg000.c).

La letra original no tiene tildes: acá se agregan á é í ó ú ñ (y sus mayúsculas),
con el acento en las dos filas de arriba que las minúsculas tienen libres. También
¿ ¡ · → ⋯ ✕, que usan los carteles.

Cada letra queda como [ancho, [filas]], con cada fila como un número (el bit más
alto es el píxel de la izquierda). Se reemplaza lo que hay entre /*FONT*/ y
/*END FONT*/ en index.html.

La misma letra también se arma como tipografía web (WOFF, normal y negrita) para
los carteles de la página: va entre /*WEBFONT*/ y /*END WEBFONT*/, como
"PoP". Cada píxel mide 1/10 de la letra: con font-size de 10, 15, 20... px los
píxeles quedan parejos. La negrita es como en la pantalla de inicio: la letra
dos veces, corrida un píxel.

Hace falta fontTools (pip install fonttools).

Uso: python3 webbuild/make_splash_font.py
"""
import base64
import io
import json
import os
import re
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT = os.path.join(ROOT, "data", "font")
HTML = os.path.join(ROOT, "webbuild", "index.html")


def glyph(code):
    path = os.path.join(FONT, f"res{1000 + code}.png")
    if not os.path.exists(path):
        return None
    im = Image.open(path)
    px = im.load()
    w, h = im.size
    return [[1 if px[x, y] else 0 for x in range(w)] for y in range(h)]


def with_accent(base, accent_rows):
    rows = [r[:] for r in base]
    w = len(rows[0])
    for y, pattern in enumerate(accent_rows):
        # el acento se centra en el ancho de la letra
        off = (w - len(pattern)) // 2
        rows[y] = [0] * w
        for i, c in enumerate(pattern):
            if c == "#" and 0 <= off + i < w:
                rows[y][off + i] = 1
    return rows


def upper_accent(base, pattern):
    # las mayúsculas usan las 7 filas: se agregan 2 arriba (el juego las dibuja desde
    # arriba, así que la letra baja; se compensa en el dibujo con "top": -2)
    w = len(base[0])
    off = (w - len(pattern)) // 2
    acc = [0] * w
    for i, c in enumerate(pattern):
        if c == "#":
            acc[off + i] = 1
    return [acc, [0] * w] + [r[:] for r in base]


def art(*rows):
    return [[1 if c == "#" else 0 for c in r] for r in rows]


# letras que no están en el juego (7 filas hasta la base; 9 si bajan como la g)
EXTRA = {
    "·": art("..", "..", "..", "##", "##", "..", ".."),
    "→": art("........", "....##..", ".....##.", "########", ".....##.", "....##..", "........"),
    "⋯": art(*["............"] * 3, "##...##...##", "##...##...##", *["............"] * 2),
    "✕": art("......", "##..##", ".####.", "..##..", ".####.", "##..##", "......"),
}


def turned(rows):
    # dada vuelta (para ¿ y ¡), bajando dos filas como la g
    w = len(rows[0])
    return [[0] * w, [0] * w] + [r[::-1] for r in rows[::-1]]


def encode(rows):
    w = len(rows[0])
    return [w, [int("".join(map(str, r)), 2) for r in rows]]


def main():
    font = {}
    for code in range(32, 127):
        g = glyph(code)
        if g:
            font[chr(code)] = encode(g)
    acute, tilde = ".##", "#.##"
    for plain, accented in zip("aeou", "áéóú"):
        font[accented] = encode(with_accent(glyph(ord(plain)), [".##", "##."]))
    i = glyph(ord("i"))
    font["í"] = encode([[0, 1], [1, 0]] + [r[:] for r in i[2:]]) if len(i[0]) == 2 else font["i"]
    n = glyph(ord("n"))
    font["ñ"] = encode(with_accent(n, ["##.#", "#.##"]))
    upper = {}
    for plain, accented in zip("AEIOU", "ÁÉÍÓÚ"):
        g = glyph(ord(plain))
        if g:
            upper[accented] = encode(upper_accent(g, acute))
    g = glyph(ord("N"))
    upper["Ñ"] = encode(upper_accent(g, tilde))
    font["\u00bf"] = encode(turned(glyph(ord("?"))))
    font["\u00a1"] = encode(turned(glyph(ord("!"))))
    for ch, rows in EXTRA.items():
        font[ch] = encode(rows)
    data = {"glyphs": font, "tall": upper, "above": 7, "line": 10, "gap": 1}
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = open(HTML, encoding="utf-8").read()
    new = re.sub(r"/\*FONT\*/.*?/\*END FONT\*/", lambda m: "/*FONT*/" + text + "/*END FONT*/", html, flags=re.S)
    if new == html and "/*FONT*/" not in html:
        raise SystemExit("index.html no tiene /*FONT*/ ... /*END FONT*/")
    css = webfont_css(data)
    newer = re.sub(r"/\*WEBFONT\*/.*?/\*END WEBFONT\*/", lambda m: "/*WEBFONT*/" + css + "/*END WEBFONT*/", new, flags=re.S)
    if "/*WEBFONT*/" not in new:
        raise SystemExit("index.html no tiene /*WEBFONT*/ ... /*END WEBFONT*/")
    open(HTML, "w", encoding="utf-8").write(newer)
    print(f"letra del juego ({len(font) + len(upper)} caracteres) -> {HTML}")


PX = 100  # unidades por píxel (la letra mide 10 píxeles: 1000 unidades)


def decode(entry):
    w, rows = entry
    return [[(bits >> (w - 1 - x)) & 1 for x in range(w)] for bits in rows]


def embolden(rows):
    """La letra dos veces, corrida un píxel. Los huecos de un píxel (la m, la w...) se
    llenarían: esas columnas se duplican antes, así el hueco sigue abierto."""
    w = len(rows[0])
    gaps = {x for r in rows for x in range(1, w - 1) if r[x - 1] and not r[x] and r[x + 1]}
    rows = [[v for x, v in enumerate(r) for _ in range(2 if x in gaps else 1)] for r in rows]
    return [[a or b for a, b in zip(r + [0], [0] + r)] for r in rows]


def outline(rows, top):
    """Los píxeles como rectángulos (tramos horizontales). top: filas sobre la base."""
    pen = TTGlyphPen(None)
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if not row[x]:
                x += 1
                continue
            end = x
            while end < len(row) and row[end]:
                end += 1
            x0, x1 = x * PX, end * PX
            y1 = (top - y) * PX
            y0 = y1 - PX
            pen.moveTo((x0, y0))
            pen.lineTo((x0, y1))
            pen.lineTo((x1, y1))
            pen.lineTo((x1, y0))
            pen.closePath()
            x = end
    return pen.glyph()


def build_font(data, bold):
    chars = {}
    for ch, entry in data["glyphs"].items():
        chars[ch] = (decode(entry), data["above"])
    for ch, entry in data["tall"].items():
        chars[ch] = (decode(entry), data["above"] + 2)
    order = [".notdef"] + [f"u{ord(ch):04X}" for ch in chars]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(ch): f"u{ord(ch):04X}" for ch in chars})
    glyphs = {".notdef": TTGlyphPen(None).glyph()}
    metrics = {".notdef": (400, 0)}
    for ch, (rows, top) in chars.items():
        name = f"u{ord(ch):04X}"
        if bold:
            rows = embolden(rows)
        glyphs[name] = outline(rows, top)
        metrics[name] = ((len(rows[0]) + data["gap"]) * PX, 0)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-200)
    style = "Bold" if bold else "Regular"
    fb.setupNameTable({"familyName": "PoP", "styleName": style})
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-200, usWinAscent=900, usWinDescent=200,
                usWeightClass=700 if bold else 400, fsSelection=0x20 if bold else 0x40)
    fb.setupPost()
    fb.font["head"].macStyle = 1 if bold else 0
    # fecha fija, para que regenerar sin cambios dé el mismo archivo
    fb.font["head"].created = fb.font["head"].modified = 0
    fb.font.recalcTimestamp = False
    fb.font.flavor = "woff"
    out = io.BytesIO()
    fb.save(out)
    return base64.b64encode(out.getvalue()).decode()


def webfont_css(data):
    faces = []
    for bold in (False, True):
        faces.append('@font-face{font-family:"PoP";font-weight:%d;font-display:block;'
                     'src:url(data:font/woff;base64,%s) format("woff")}'
                     % (700 if bold else 400, build_font(data, bold)))
    return "".join(faces)


if __name__ == "__main__":
    main()
