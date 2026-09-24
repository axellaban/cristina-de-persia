#!/usr/bin/env python3
"""Mauricio: perfil propio, chaleco, mangas arremangadas y capa del visir.

Las piernas y la capa conservan las siluetas animadas originales. El torso y
el brazo se dibujan entre el cuello, el cinturon y la mano de cada fotograma.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from make_kid import components

ROOT = Path(__file__).resolve().parents[3]
DST = ROOT / 'mods/CristinaOfPersia/data'
T, PANTS, PANTS_D, WHITE, EYE, SKIN_D, SKIN, OLD_BEARD, CAPE_D, CAPE, SHOE_D, SHOE, HAIR, SHIRT, GOLD, HAIR_D, VEST, VEST_D, BELT, SHIRT_D, CAPE_H = range(21)
COLORS = {
    T:(0,0,0), PANTS:(215,199,159), PANTS_D:(167,148,110),
    WHITE:(234,239,235), EYE:(77,164,215), SKIN_D:(184,128,100), SKIN:(239,186,145),
    OLD_BEARD:(239,186,145), CAPE_D:(73,14,35), CAPE:(137,25,57), CAPE_H:(168,35,68),
    SHOE_D:(35,29,25), SHOE:(65,52,39), HAIR:(141,143,137), HAIR_D:(89,93,90),
    SHIRT:(151,199,227), SHIRT_D:(102,153,187), GOLD:(194,160,83),
    VEST:(29,47,81), VEST_D:(17,28,50), BELT:(111,66,36),
}
HEAD = (
    '..gggg...', '.dggggg..', '.dggsss..', '.dssses..',
    '..ssssss.', '..sssss..', '...swqs..', '...ssq...', '...ss....',
)
HEAD_COLORS = {'.':T,'g':HAIR,'d':HAIR_D,'s':SKIN,'e':EYE,'w':WHITE,'q':SKIN_D}


def set_palette(im):
    pal=[0]*768
    for index,rgb in COLORS.items():
        pal[index*3:index*3+3]=rgb
    im.putpalette(pal)
    im.info['transparency']=0
    return im


def landmarks(im):
    px=im.load()
    w,h=im.size
    groups=components(px,w,h,{12,13,15})
    if not groups:
        return None
    hat=min(groups,key=lambda c:min(y for x,y in c))
    top=min(y for x,y in hat)
    hx=sum(x for x,y in hat)/len(hat)
    candidates=[(x,y) for y in range(top+3,min(h,top+10)) for x in range(w)
                if px[x,y] in (4,5,6) and abs(x-hx)<7]
    eyes=[p for p in candidates if px[p]==4]
    if not candidates:
        return hat,None,None,None,None
    face_x=sum(x for x,y in candidates)/len(candidates)
    facing=1 if face_x>hx else -1
    if eyes:
        eye=eyes[0]
    else:
        cape=[x for y in range(top+9,min(h,top+18)) for x in range(w) if px[x,y]==9]
        if cape:
            facing=-1 if sum(cape)/len(cape)>hx else 1
        fy=min(y for x,y in candidates)
        row=[x for x,y in candidates if y==fy]
        eye=(max(row) if facing>0 else min(row),fy)
    belt=[p for c in groups if c is not hat for p in c if p[1]>eye[1]+6]
    waist=min((y for x,y in belt),default=eye[1]+15)
    return hat,eye,facing,belt,waist


def draw_head(im,eye,facing):
    px=im.load()
    for y,row in enumerate(HEAD):
        for x,symbol in enumerate(row):
            if symbol=='.':
                continue
            xx,yy=eye[0]+(x-5)*facing,eye[1]+y-3
            if 0<=xx<im.width and 0<=yy<im.height:
                px[xx,yy]=HEAD_COLORS[symbol]


def transform(original):
    if original.size == (1,1):
        return set_palette(Image.new('P',(1,1),T))
    marks=landmarks(original)
    if marks is None:
        # Fotogramas vacios y efectos: no pertenecen al cuerpo.
        return original.copy()
    hat,eye,facing,belt,waist=marks
    w,h=original.size
    src=original.load()
    out=set_palette(Image.new('P',(w,h),T))
    px=out.load()
    if h<=20:
        return fallen(original)
    occluded=False
    if eye is None and any(src[x,y] in (5,6) for y in range(h) for x in range(w)):
        top=min(y for x,y in hat)
        eye=(min(x for x,y in hat)+2,top+4)
        facing=-1
        groups=components(src,w,h,{12,13,15})
        belt=[p for c in groups for p in c if p[1]>eye[1]+5]
        waist=min((y for x,y in belt),default=eye[1]+15)
        occluded=True
    if eye is None:
        for y in range(h):
            for x in range(w):
                if src[x,y] in (8,9):
                    px[x,y]=CAPE
                elif src[x,y] in (1,2,10,11):
                    px[x,y]=src[x,y]
        top=min(y for x,y in hat)
        cx=round(sum(x for x,y in hat)/len(hat))
        draw=ImageDraw.Draw(out)
        draw.rounded_rectangle((cx-3,top+2,cx+2,top+7),radius=1,fill=HAIR_D)
        draw.line((cx-2,top+2,cx+1,top+2),fill=HAIR)
        return out
    ex,ey=eye
    neck=(ex-2*facing,ey+5)
    if belt:
        front=max(x for x,y in belt) if facing>0 else min(x for x,y in belt)
        hip=(front-2*facing,waist)
    else:
        hip=(neck[0],waist)
    # Siluetas originales de capa y pantalon, con pliegues ligados al borde.
    for y in range(h):
        cape=[x for x in range(w) if src[x,y] in (8,9)]
        rear=(min(cape) if facing>0 else max(cape)) if cape else None
        for x in range(w):
            color=src[x,y]
            if color in (8,9):
                depth=(x-rear)*facing
                px[x,y]=CAPE_D if depth<2 else CAPE
                if depth==2:
                    px[x,y]=CAPE_H
            elif color in (1,2) and y>=waist:
                px[x,y]=PANTS if color==1 else PANTS_D
            elif color in (10,11):
                px[x,y]=SHOE_D if color==10 else SHOE
            elif color==3:
                px[x,y]=WHITE
    draw=ImageDraw.Draw(out)
    sx,sy=neck
    hx,hy=hip
    for y in range(sy,hy+1):
        t=(y-sy)/max(1,hy-sy)
        cx=round(sx+(hx-sx)*t)
        half=2 if y==sy else 3
        draw.line((cx-half,y,cx+half,y),fill=VEST)
        draw.point((cx-3*facing,y),fill=VEST_D)
        if y in (sy+5,sy+9):
            draw.line((cx-2,y,cx+2,y),fill=VEST_D)
        draw.point((cx+2*facing,y),fill=SHIRT_D if y<sy+3 else VEST_D)
    draw.line((hx-3,hy,hx+3,hy),fill=BELT)
    draw.point((hx+2*facing,hy),fill=GOLD)
    # La mano original fija el extremo del brazo. Las poses sin mano visible
    # usan un brazo relajado junto al cuerpo, nunca una manga vacia.
    hands=[(x,y) for y in range(min(h,waist)) for x in range(w) if src[x,y] in (5,6)
           and (abs(x-ex)>6 or y<ey-4 or y>ey+6)]
    shoulder=(sx-facing,sy+2)
    if hands:
        tip=max(hands,key=lambda p:(p[0]-shoulder[0])**2+(p[1]-shoulder[1])**2)
        cluster=[p for p in hands if max(abs(p[0]-tip[0]),abs(p[1]-tip[1]))<=2]
        hand=(round(sum(x for x,y in cluster)/len(cluster)),round(sum(y for x,y in cluster)/len(cluster)))
    else:
        hand=(hx+2*facing,hy-2)
    ax,ay=hand
    if ay<sy:
        elbow=(round((shoulder[0]+ax)/2),round((shoulder[1]+ay)/2))
    else:
        elbow=(round(shoulder[0]+(ax-shoulder[0])*.3),round(sy+(ay-sy)*.65))
    if occluded:
        draw_head(out,eye,facing)
    draw.line([shoulder,elbow],fill=SHIRT_D,width=4)
    draw.line([(shoulder[0]+facing,shoulder[1]),(elbow[0]+facing,elbow[1])],fill=SHIRT,width=2)
    draw.line([elbow,hand],fill=SKIN_D,width=3)
    draw.line([(elbow[0]+facing,elbow[1]),hand],fill=SKIN,width=2)
    draw.rectangle((elbow[0]-1,elbow[1]-1,elbow[0]+1,elbow[1]),fill=SHIRT)
    draw.rectangle((ax-1,ay-1,ax+1,ay+1),fill=SKIN)
    if not occluded:
        draw_head(out,eye,facing)
    return out


def fallen(original):
    """Caida horizontal: preserva la silueta y el arma, sin un torso vertical."""
    out=set_palette(original.copy())
    src,px=original.load(),out.load()
    w,h=out.size
    hat=[(x,y) for y in range(h) for x in range(w) if src[x,y] in (12,13,15)]
    head_x=max((x for x,y in hat),default=w-1)-4
    for y in range(h):
        for x in range(w):
            color=src[x,y]
            if color in (12,13,15):
                px[x,y]=HAIR_D if y>h//2 else HAIR
            elif color==7:
                px[x,y]=CAPE_D
            elif color in (1,2) and x>head_x-12:
                px[x,y]=VEST if color==1 else VEST_D
            elif color==9:
                px[x,y]=CAPE
    return out


BALLOON = [
    '...yyyyy...', '..yYYyyyy..', '.yYYyyyyyy.', '.yYyyyyyyyo',
    'yyyyyyyyyyo', 'yyyyyyyyyyo', 'yyyyyyyyyyo', '.yyyyyyyyo.',
    '.yyyyyyyoo.', '..yyyyyoo..', '...yyoo....', '....oo.....',
    '.....s.....', '....s......', '....s......', '.....s.....',
    '......s....', '......s....', '.....s.....',
]
BALLOON_COLORS = {'.':(0,0,0),'y':(252,214,0),'Y':(255,246,170),'o':(206,158,0),'s':(230,230,230)}


def balloon():
    keys=list(BALLOON_COLORS)
    im=Image.new('P',(len(BALLOON[0]),len(BALLOON)),0)
    pal=[c for k in keys for c in BALLOON_COLORS[k]]
    im.putpalette(pal+[0]*(768-len(pal)))
    for y,row in enumerate(BALLOON):
        for x,ch in enumerate(row):
            im.putpixel((x,y),keys.index(ch))
    im.save(DST/'PV/res963.png',transparency=0)
    pal=bytearray((ROOT/'data/PV/res950.pal').read_bytes())
    pal[0]=13
    (DST/'PV/res950.pal').write_bytes(pal)


def main():
    for folder,ids in (('PV',range(851,889)),('VIZIER',range(751,785))):
        (DST/folder).mkdir(parents=True,exist_ok=True)
        for resource in ids:
            original=Image.open(ROOT/'data'/folder/f'res{resource}.png')
            result=original.copy() if folder=='VIZIER' and resource in (751,752) else transform(original)
            result.save(DST/folder/f'res{resource}.png',transparency=0)
        print(f'{len(ids)} frames -> {DST/folder}')
    balloon()


if __name__=='__main__':
    main()
