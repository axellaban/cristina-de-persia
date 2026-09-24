#!/usr/bin/env python3
"""Mete la letra del juego (data/font) en webbuild/index.html, para la pantalla de
inicio de la web: la misma letra y el mismo armado que la pantalla de inicio de
SDLPoP (show_splash en src/seg000.c).

La letra original no tiene tildes: acá se agregan á é í ó ú ñ (y sus mayúsculas),
con el acento en las dos filas de arriba que las minúsculas tienen libres.

Cada letra queda como [ancho, [filas]], con cada fila como un número (el bit más
alto es el píxel de la izquierda). Se reemplaza lo que hay entre /*FONT*/ y
/*END FONT*/ en index.html.

Uso: python3 webbuild/make_splash_font.py
"""
import json
import os
import re
from PIL import Image

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
    data = {"glyphs": font, "tall": upper, "above": 7, "line": 10, "gap": 1}
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = open(HTML, encoding="utf-8").read()
    new = re.sub(r"/\*FONT\*/.*?/\*END FONT\*/", lambda m: "/*FONT*/" + text + "/*END FONT*/", html, flags=re.S)
    if new == html and "/*FONT*/" not in html:
        raise SystemExit("index.html no tiene /*FONT*/ ... /*END FONT*/")
    open(HTML, "w", encoding="utf-8").write(new)
    print(f"letra del juego ({len(font) + len(upper)} caracteres) -> {HTML}")


if __name__ == "__main__":
    main()
