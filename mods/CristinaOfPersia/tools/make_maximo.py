#!/usr/bin/env python3
"""Pixel art de Maximo sobre las coordenadas locales de las poses PV originales.

Cada pose define ojo, cadera, manos y tobillos. No se escala el fotograma.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'data/PV'
DST = ROOT / 'mods/CristinaOfPersia/data/PV'

T, HAIR, GRAY, SKIN, SKIN_D, EYE, BEARD, WHITE, BLUE, BLUE_D, BLUE_H, DENIM, DENIM_D, SOLE, SKIN_H, LIPS, BROWN, BROWN_D, SUIT, SUIT_D, SASH, GOLD = range(22)
COLORS = {
    T: (0, 0, 0), HAIR: (62, 54, 47), GRAY: (114, 113, 106),
    SKIN: (232, 170, 132), SKIN_D: (169, 107, 84), SKIN_H: (248, 196, 153),
    EYE: (37, 31, 28), BEARD: (94, 77, 62), WHITE: (234, 240, 241),
    BLUE: (43, 151, 217), BLUE_D: (24, 99, 166), BLUE_H: (103, 191, 235),
    DENIM: (51, 82, 139), DENIM_D: (32, 53, 94), SOLE: (155, 168, 183),
    LIPS: (190, 38, 56), BROWN: (109, 58, 34), BROWN_D: (63, 33, 23),
    SUIT: (40, 68, 160), SUIT_D: (26, 32, 92), SASH: (116, 184, 236), GOLD: (236, 184, 40),
}

# Ojo, direccion, cadera, mano lejana, mano cercana, tobillo lejano, tobillo cercano.
POSES = {
    801: ((4,4), -1, (9,23), (13,24), (2,16), (10,40), (8,40)),
    802: ((5,4), -1, (9,23), (12,16), (1,16), (10,40), (8,40)),
    803: ((8,4), -1, (9,23), (13,16), (3,16), (10,40), (8,40)),
    804: ((9,4),  1, (9,23), (1,16), (12,14), (7,39), (10,39)),
    805: ((9,4),  1, (10,23), (3,16), (11,16), (3,39), (12,38)),
    806: ((18,4), 1, (13,23), (9,16), (19,16), (10,39), (21,39)),
    807: ((17,4), 1, (14,23), (1,10), (19,16), (12,39), (18,40)),
    808: ((12,4), 1, (9,23), (2,12), (14,16), (6,39), (11,40)),
    809: ((14,4), 1, (10,23), (9,23), (16,16), (9,40), (11,40)),
    810: ((15,4), 1, (11,23), (11,24), (16,18), (9,40), (13,40)),
    811: ((17,4), 1, (12,23), (13,23), (9,24), (15,39), (2,40)),
    812: ((14,4), 1, (10,23), (11,22), (3,23), (16,39), (4,40)),
    813: ((16,4), 1, (13,23), (14,22), (9,24), (22,39), (10,40)),
    814: ((14,4), 1, (12,23), (12,23), (9,24), (15,39), (11,40)),
    815: ((15,4), 1, (12,23), (12,23), (11,24), (12,40), (10,40)),
    816: ((16,5), 1, (12,23), (12,23), (11,24), (12,40), (10,40)),
    817: ((16,5), 1, (12,23), (12,23), (11,24), (12,40), (10,40)),
    901: ((8,4),  1, (22,15), (4,17), (15,14), (44,22), (40,22)),
    903: ((4,3), -1, (7,20), (6,17), (2,14), (5,36), (4,36)),
    904: ((8,3),  1, (7,21), (6,16), (10,17), (4,37), (6,37)),
    905: ((12,3), 1, (9,21), (6,15), (13,15), (6,35), (9,36)),
    906: ((15,3), 1, (11,20), (8,16), (15,15), (6,35), (12,35)),
    907: ((16,3), 1, (12,20), (9,17), (14,15), (6,34), (14,34)),
    908: ((22,3), 1, (18,20), (17,20), (20,17), (9,34), (20,34)),
    909: ((21,3), 1, (19,19), (18,19), (22,15), (4,33), (25,33)),
    910: ((23,4), 1, (20,20), (25,18), (30,13), (5,31), (23,33)),
    911: ((20,6), 1, (15,23), (31,17), (29,11), (12,37), (15,37)),
    912: ((19,4), 1, (13,23), (25,13), (25,10), (7,37), (20,37)),
    913: ((17,5), 1, (12,23), (21,13), (22,10), (7,35), (15,37)),
    914: ((12,5), 1, (8,23), (16,12), (17,10), (3,36), (10,36)),
    915: ((11,6), 1, (7,24), (15,12), (16,10), (2,36), (10,36)),
    916: ((10,6), 1, (7,23), (14,12), (15,10), (2,35), (10,36)),
    917: ((20,4), 1, (15,18), (15,14), (29,12), (3,20), (7,20)),
    918: ((20,4), 1, (15,18), (13,14), (27,13), (3,20), (7,20)),
    919: ((20,4), 1, (15,18), (13,14), (24,14), (3,20), (7,20)),
    920: ((20,4), 1, (15,18), (13,14), (22,14), (3,20), (7,20)),
    921: ((20,4), 1, (15,19), (15,15), (21,14), (4,22), (9,22)),
    922: ((20,4), 1, (14,19), (13,15), (19,15), (4,22), (8,22)),
    923: ((25,4), 1, (19,20), (16,15), (22,15), (5,23), (11,23)),
    924: ((21,4), 1, (16,20), (13,17), (20,17), (4,24), (14,24)),
    925: ((26,4), 1, (21,22), (20,20), (27,19), (9,27), (20,27)),
    926: ((24,4), 1, (20,22), (18,23), (25,21), (9,30), (16,30)),
    927: ((20,4), 1, (17,22), (15,20), (23,19), (12,33), (15,33)),
    928: ((20,4), 1, (17,22), (16,19), (25,18), (15,35), (17,35)),
    929: ((20,4), 1, (17,23), (16,17), (25,16), (15,37), (17,37)),
    930: ((19,4), 1, (16,23), (15,16), (21,15), (14,39), (16,39)),
}

# Perfil dibujado a mano hacia la derecha; ojo en (5, 3).
HEAD = (
    '.hhhhh...', 'hhghhhh..', 'hhgsss...', 'hhsses...', 'hgsssss..',
    'hhssbbs..', '.hssswq..', '.hh.sq...', '...ss....',
)
HEAD_COLORS = {'.':T, 'h':HAIR, 'g':GRAY, 's':SKIN, 'e':EYE, 'b':BEARD, 'w':WHITE, 'q':SKIN_D}


def canvas(size):
    im = Image.new('P', size, T)
    pal = [0] * 768
    for index, color in COLORS.items():
        pal[index * 3:index * 3 + 3] = color
    im.putpalette(pal)
    im.info['transparency'] = T
    return im


def head(im, eye, facing, rear=False):
    px = im.load()
    for y, row in enumerate(HEAD):
        for x, symbol in enumerate(row):
            if symbol == '.':
                continue
            xx, yy = eye[0] + (x - 5) * facing, eye[1] + y - 3
            if 0 <= xx < im.width and 0 <= yy < im.height:
                color = HEAD_COLORS[symbol]
                if rear and y < 7:
                    color = GRAY if x == 2 and y in (2,3) else HAIR
                px[xx, yy] = color


def arm(draw, shoulder, hand, facing, far=False):
    sx, sy = shoulder
    hx, hy = hand
    elbow = (round(sx + (hx - sx) * .55 - facing), round(sy + (hy - sy) * .55 + 1))
    draw.line([shoulder, elbow, hand], fill=BLUE_D, width=4)
    draw.line([shoulder, elbow, (hx,hy-1)], fill=BLUE if not far else BLUE_D, width=2)
    if not far:
        stripe = [(sx-facing,sy-1), (elbow[0]-facing,elbow[1]-1), (hx-facing,hy-2)]
        draw.line(stripe, fill=WHITE, width=1)
    draw.rectangle((hx-1,hy-1,hx+1,hy+1), fill=SKIN_D if far else SKIN)
    if not far:
        draw.point((hx+facing,hy-1), fill=SKIN_H)


def leg(draw, hip, knee, ankle, facing, far=False):
    draw.line([hip,knee,ankle], fill=DENIM_D, width=5)
    draw.line([(hip[0],hip[1]+1),knee,ankle], fill=DENIM_D if far else DENIM, width=3)
    ax, ay = ankle
    toe = ax + 3*facing
    lo, hi = min(ax-1,toe), max(ax+1,toe)
    draw.rectangle((lo,ay,hi,ay+1), fill=SOLE if far else WHITE)
    draw.line((lo,ay+2,hi,ay+2), fill=SOLE)


def torso(draw, eye, hip, facing):
    sx, sy = eye[0]-2*facing, eye[1]+5
    hx, hy = hip
    # Hombros caidos, abdomen redondeado y dobladillo recto.
    fronts = (1,2,3,3,3,4,4,5,5,5,4,4,3)
    backs = (2,3,4,4,4,4,4,4,4,4,3,3,3)
    for y in range(sy,hy+1):
        t = (y-sy)/max(1,hy-sy)
        k = min(12,round(t*12))
        cx = round(sx+(hx-sx)*t)
        rear, front = cx-backs[k]*facing, cx+fronts[k]*facing
        lo,hi = sorted((rear,front))
        draw.line((lo,y,hi,y),fill=BLUE_D if y==hy else BLUE)
        draw.point((rear,y),fill=BLUE_D)
        if y < hy-1:
            draw.point((front-facing,y),fill=BLUE_H)
        if sy+2 <= y <= sy+4:
            draw.point((cx-2*facing,y),fill=WHITE)
    draw.line((sx-1,sy,sx+1,sy), fill=BLUE_D)


def render(im, resource):
    eye, facing, hip, far_hand, hand, far_ankle, ankle = POSES[resource]
    out = canvas(im.size)
    draw = ImageDraw.Draw(out)
    shoulder = (eye[0]-2*facing,eye[1]+7)
    seated = 917 <= resource <= 925
    for far, foot in ((True,far_ankle),(False,ankle)):
        start = (hip[0]+(-1 if far else 1),hip[1])
        if seated:
            knee = (min(im.width-3,hip[0]+6),min(im.height-3,hip[1]+3))
            if far:
                knee = (knee[0]-3,knee[1]-1)
        elif resource == 901:
            knee = (30,11 if far else 12)
        else:
            knee = (round((start[0]+foot[0])/2)+facing,round((start[1]+foot[1])/2))
        leg(draw,start,knee,foot,facing,far)
    arm(draw,shoulder,far_hand,facing,True)
    torso(draw,eye,hip,facing)
    arm(draw,shoulder,hand,facing)
    head(out,eye,facing,rear=resource in (803,804,805))
    return out


def embrace(original, resource):
    """Maximo conserva su modelo; Cristina se superpone con la oclusion original."""
    out = render(original, resource)
    src, px = original.load(), out.load()
    w,h = out.size
    mapping = {1:BROWN,2:EYE,7:BROWN_D,3:SUIT,12:SUIT_D,13:BROWN_D,
               14:EYE,5:SKIN_D,6:SKIN}
    max_eye = POSES[resource][0]
    kid_hair=[(x,y) for y in range(h) for x in range(w) if src[x,y]==1]
    kid_left=min(x for x,y in kid_hair)
    kid_top=min(y for x,y in kid_hair)
    for y in range(h):
        for x in range(w):
            color=src[x,y]
            if color in (1,2,3,12,13) or (color==7 and x>=kid_left):
                px[x,y]=mapping[color]
            elif color in (5,6,14) and x>=max_eye[0]+1 and y<kid_top+14:
                px[x,y]=mapping[color]
    # Pelo hasta los hombros y manga azul en el brazo superior de Cristina.
    for x,y in kid_hair:
        if x>=kid_left+4:
            for dy in range(1,6):
                if y+dy<h and px[x,y+dy] in (T,SUIT,SUIT_D):
                    px[x,y+dy]=BROWN_D
    for y in range(kid_top+8,min(h,kid_top+13)):
        for x in range(max_eye[0]+4,w):
            if px[x,y] in (SKIN,SKIN_D):
                px[x,y]=SUIT
    rows = []
    for y in range(h):
        xs = [x for x in range(w) if px[x,y] in (SUIT,SUIT_D)]
        if len(xs)>=3:
            rows.append((y,min(xs),max(xs)))
    for k,(y,lo,hi) in enumerate(rows[:12]):
        x=round(lo+(hi-lo)*k/max(1,min(12,len(rows))-1))
        px[x,y]=SASH
        if x+1<=hi and px[x+1,y] in (SUIT,SUIT_D):
            px[x+1,y]=WHITE
    return out


def main():
    DST.mkdir(parents=True,exist_ok=True)
    for resource in sorted(POSES):
        original=Image.open(SRC/f'res{resource}.png')
        result=embrace(original,resource) if 911<=resource<=916 else render(original,resource)
        result.save(DST/f'res{resource}.png',transparency=T)
    print(f'{len(POSES)} frames -> {DST}')


if __name__=='__main__':
    main()
