#!/usr/bin/env python3
"""Pantallas de título e historia de Cristina of Persia.

- TITLE/res54: logo "CRISTINA of PERSIA" (reemplaza "PRINCE of PERSIA")
- TITLE/res52: "Una parodia argentina" (reemplaza "Broderbund Software presents")
- TITLE/res53: "a game by Axel Laban & Jordan Mechner" (reemplaza "a game by Jordan Mechner")
  Estas dos usan la tipografía de los créditos originales (title_font.py).
- TITLE/res42, 43, 44: textos de la historia, en castellano
Los créditos del juego original (res45 y el copyright de Jordan Mechner, res55) no se tocan.

Cada imagen conserva tamaño y paleta del original: el juego las dibuja en
posiciones fijas.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import title_font

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "data", "TITLE")
DST = os.path.join(ROOT, "mods", "CristinaOfPersia", "data", "TITLE")
FONTS = "/System/Library/Fonts/Supplemental"
# Dónde buscar las fuentes: macOS, las "core fonts" de Microsoft instaladas en Linux
# (ttf-mscorefonts-installer) o una carpeta propia en la variable TITLE_FONTS.
FONT_DIRS = [os.environ.get("TITLE_FONTS", ""), FONTS, "/usr/share/fonts/truetype/msttcorefonts"]
FONT_NAMES = {"Georgia Bold.ttf": ["Georgia Bold.ttf", "Georgia_Bold.ttf", "georgiab.ttf", "Georgiab.TTF"]}

STORIES = {
    42: ("E", "n ausencia del Pueblo, el Gran Visir MAURICIO gobierna con mano "
              "de hierro y globos amarillos. Sólo un obstáculo lo separa del "
              "trono: el hijo de la Reina, el joven Máximo..."),
    43: ("A", "filiarse al PRO... o morir antes de que termine la hora. Todas "
              "las esperanzas de Máximo están puestas en la mujer que más lo "
              "quiere: su madre. Lo que no sabe es que ella ya está presa en "
              "los calabozos de Mauricio..."),
    44: ("E", "l tirano Mauricio yace derrotado, sus globos pinchados. En toda la "
              "tierra el pueblo aclama a Máximo... y a la heroína que lo "
              "rescató. Desde hoy y para siempre se la conocerá como... "
              "CRISTINA OF PERSIA."),
}


def find_font(name):
    for d in filter(None, FONT_DIRS):
        for n in FONT_NAMES.get(name, [name]):
            if os.path.exists(os.path.join(d, n)):
                return os.path.join(d, n)
    return None


def font(name, size, index=0):
    return ImageFont.truetype(find_font(name), size, index=index, layout_engine=ImageFont.Layout.BASIC)


def wrap(draw, words, fnt, widths):
    """Reparte las palabras en líneas; widths(i) da el ancho de la línea i."""
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= widths(len(lines)):
            cur = test
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def layout(res, cap, text, size):
    ref = Image.open(os.path.join(SRC, f"res{res}.png"))
    w, h = ref.size
    body = font("Georgia Bold.ttf", size)
    big = font("Georgia Bold.ttf", size * 2 + 6)
    img = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    cap_w = d.textlength(cap, font=big) + 3
    lines = wrap(d, text.split(), body, lambda i: w - (cap_w if i < 2 else 0))
    return ref, img, d, body, big, cap_w, lines, (len(lines) * (size + 2) <= h)


def story(res, cap, text, size):
    ref, img, d, body, big, cap_w, lines, _ = layout(res, cap, text, size)
    w, h = ref.size
    lh = size + 2
    d.text((0, -size // 3), cap, font=big, fill=1)
    for i, line in enumerate(lines):
        x = cap_w if i < 2 else 0
        d.text((x, i * lh), line, font=body, fill=1)
    out = Image.new("P", (w, h), 0)
    out.putpalette(ref.getpalette())
    out.paste(1, mask=img)
    out.save(os.path.join(DST, f"res{res}.png"), transparency=0)
    print(f"res{res}: {len(lines)} líneas, cuerpo {size}px")


def outlined(mask, fill_idx, line_idx, size, palette):
    """Texto con relleno y contorno de 1 px, como el logo original."""
    edge = mask.filter(ImageFilter.MaxFilter(3))
    out = Image.new("P", size, 0)
    out.putpalette(palette)
    out.paste(line_idx, mask=edge)
    out.paste(fill_idx, mask=mask)
    return out


def logo():
    ref = Image.open(os.path.join(SRC, "res54.png"))
    w, h = ref.size
    S = 4  # se dibuja grande y se reduce para que las letras queden prolijas
    big = Image.new("L", (w * S * 3, h * S), 0)
    d = ImageDraw.Draw(big)
    f_big = font("Herculanum.ttf", 44 * S)
    f_of = font("Herculanum.ttf", 20 * S)
    left, right = "CRISTINA", "PERSIA"
    wl = d.textlength(left, font=f_big)
    wo = d.textlength("of", font=f_of)
    wr = d.textlength(right, font=f_big)
    gap = 3 * S
    x = 0
    d.text((x, 6 * S), left, font=f_big, fill=255)
    x += wl + gap
    d.text((x, 30 * S), "of", font=f_of, fill=255)
    x += wo + gap
    d.text((x, 6 * S), right, font=f_big, fill=255)
    bbox = big.getbbox()
    crop = big.crop(bbox)
    target_w, target_h = w - 4, h - 4
    # se comprime en horizontal lo justo para que entre, sin perder altura
    nh = target_h
    nw = min(target_w, int(crop.width * nh / crop.height))
    small = crop.resize((nw, nh), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0).convert("1")
    mask = Image.new("1", (w, h), 0)
    mask.paste(small, ((w - nw) // 2, (h - nh) // 2))
    out = outlined(mask, 15, 1, (w, h), ref.getpalette())
    out.save(os.path.join(DST, "res54.png"), transparency=0)
    print("res54: logo")


def credit(res, pos, width, lines):
    """Crédito con la tipografía del título original, sobre el fondo del palacio
    (las imágenes originales traen ese pedazo de fondo incorporado)."""
    ref = Image.open(os.path.join(SRC, f"res{res}.png"))
    bg = Image.open(os.path.join(SRC, "res51.png"))
    x, y = pos
    crop = bg.crop((x, y, x + width, y + ref.size[1]))
    out = title_font.credit_image(crop, lines, white=15, black=0)
    out.save(os.path.join(DST, f"res{res}.png"))
    print(f"res{res}: " + " / ".join(t for t, _ in lines))


def presents():
    # se dibuja en (96, 106), como el original
    credit(52, (96, 106), 128, [("Una parodia", 10), ("argentina", 26)])


AUTHORS = "Axel Laban & Jordan Mechner"


def author():
    # más ancha que la original (122 px): el juego la centra en el mismo lugar
    # (ver draw_full_image en src/seg000.c, que hace xpos += (122 - ancho) / 2)
    width = title_font.text_width(AUTHORS) + 6
    x = 96 + int((122 - width) / 2)  # división de C: trunca hacia cero
    credit(53, (x, 122), width, [("a game by", 4), (AUTHORS, 18)])


def main():
    os.makedirs(DST, exist_ok=True)
    author()     # tipografía propia (title_font.py)
    presents()
    if find_font("Georgia Bold.ttf"):
        # el mismo tamaño de letra en las tres pantallas: el mayor que entre en todas
        size = next(sz for sz in range(15, 9, -1)
                    if all(layout(r, c, t, sz)[-1] for r, (c, t) in STORIES.items()))
        for res, (cap, text) in STORIES.items():
            story(res, cap, text, size)
    else:
        print("(sin Georgia: la historia queda como está; ver FONT_DIRS)")
    if find_font("Herculanum.ttf"):
        logo()
    else:
        print("(sin Herculanum, de macOS: el logo queda como está)")


if __name__ == "__main__":
    main()
