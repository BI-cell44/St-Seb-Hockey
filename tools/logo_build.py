from PIL import Image,ImageFilter
import numpy as np, math
from scipy import ndimage
SRC='/mnt/user-data/uploads/476fbafe-image.png'
im=Image.open(SRC).convert('RGB');W,H=im.size;src=im.load()
def avg(pts):
    cs=[src[x,y] for x,y in pts];return tuple(sum(c[i] for c in cs)//len(cs) for i in range(3))
INT=avg([(x,y) for x in range(285,295) for y in range(135,150)]+[(x,y) for x in range(350,372) for y in range(195,210)])
INTB=avg([(x,y) for x in range(205,235) for y in range(405,425)])
BL=avg([(x,y) for x in range(408,413) for y in range(195,215)])
WH=(250,252,248);OR=avg([(x,y) for x in range(385,390) for y in range(195,215)]);BG=(255,255,255)
COL=[BG,BL,WH,OR,INT]
PAD=16;H2=500
out=Image.new('RGB',(W,H2+PAD),BG);out.paste(im,(0,PAD));p=out.load()
def P(x,y): return p[x,y+PAD]
def S(x,y,c): p[x,y+PAD]=c
# ---- coin haut-droit (castor) ----
def layer(x,y):
    d=y-(118+0.55*(x-304))
    lt=4 if d>=10 else 3 if d>=0 else 2 if d>=-18 else 1 if d>=-30 else 0
    e=(392+(190-y)*0.15)-x
    lr=4 if e>=9 else 3 if e>=0 else 2 if e>=-15.5 else 1 if e>=-25 else 0
    return min(lt,lr)
def intcol(x,y):
    c=src[292,y]
    if not(c[2]>120 and c[0]<80): return INT
    t=min(1,max(0,(x-293)/40));return tuple(round(c[i]*(1-t)+INT[i]*t) for i in range(3))
def sub_top(x,y):
    ri=math.hypot(x-220.6,y-88.7);ro=math.hypot(x-221.2,y-89.5)
    if ri<=77: return None
    if ro<=85.4: return BL
    if ro<=88.5 and layer(x,y)<4: return WH
    if 288<=x<=330 and y>=173+0.0177*(x-288)**2: return WH
    l=layer(x,y);return intcol(int(x),int(y)) if l==4 else COL[l]
SS=[(i/3-1/3,j/3-1/3) for i in range(3) for j in range(3)]
def aa(f,x,y,orig):
    acc=[0,0,0]
    for dx,dy in SS:
        c=f(x+dx,y+dy)
        if c is None: c=orig
        acc=[a+b for a,b in zip(acc,c)]
    return tuple(a//len(SS) for a in acc)
for y in range(0,191):
    for x in range(293,W):
        if 255<=x<330 and y>=173+0.0177*(x-288)**2-3 and sum(src[x,y])>660: continue
        S(x,y,aa(sub_top,x,y,src[x,y]))
# ---- bas du bouclier (géométrie) ----
kL,bL=1.0907,-337.9; kR,bR=-1.0924,779.0; TX,TY,CK=220,485,2.2
nL=math.sqrt(1+kL*kL);nR=math.sqrt(1+kR*kR);nC=math.sqrt(1+1/CK**2)
def dist(x,y):
    dl=(x-(kL*y+bL))/nL; dr=((kR*y+bR)-x)/nR
    dc=(TY-abs(x-TX)/CK-y)/nC
    return min(dl,dr,dc)
def stick(x,y):
    a=abs(x-(182.5-(y-396)*0.226)); b=abs(x-(255.5+(y-396)*0.214))
    return min(a-4.8,b-4.3)
BLB=(5,42,205);ORB=(249,102,12)
def sub_bot(x,y):
    d=dist(x,y)
    if d<0: return BG
    if d<9: return BLB
    s=stick(x,y)
    if s<0: return WH
    if s<5.5 and d>=10.5: return BLB
    if d<22.5: return WH
    if d<30.5: return ORB
    return INTB
Y0,Y1=434,446
for y in range(Y0,H2):
    for x in range(W):
        c=aa(sub_bot,x,y,None)
        if y<=Y1:
            t=(y-Y0)/(Y1-Y0);o=P(x,y);c=tuple(round(o[q]*(1-t)+c[q]*t) for q in range(3))
        S(x,y,c)
out.save('/tmp/logo/clean.png')
# ---- transparence : contour blanc net d'épaisseur fixe ----
A=np.asarray(out).astype(int)
colored=(A.min(2)<200)|((A.max(2)-A.min(2))>45)
colored=ndimage.binary_opening(colored,iterations=1)
yy,xx=np.mgrid[-10:11,-10:11];disk=(xx*xx+yy*yy)<=100
closed=ndimage.binary_closing(np.pad(colored,12),structure=disk)[12:-12,12:-12]
filled=ndimage.binary_fill_holes(closed)
lab,nl=ndimage.label(filled);sizes=ndimage.sum(filled,lab,range(1,nl+1));filled=lab==(1+int(np.argmax(sizes)))
filled=ndimage.binary_fill_holes(filled)
# distance (sur-échantillonnée x4 pour un bord lisse)
up=np.asarray(Image.fromarray((filled*255).astype('uint8')).resize((filled.shape[1]*4,filled.shape[0]*4),Image.BILINEAR))>127
dist4=ndimage.distance_transform_edt(~up)/4
R=7
alpha4=np.clip(R+0.5-dist4,0,1)
alpha=np.asarray(Image.fromarray((alpha4*255).astype('uint8')).resize((filled.shape[1],filled.shape[0]),Image.BOX))
o=out.convert('RGBA');o.putalpha(Image.fromarray(alpha));o=o.crop(o.getbbox())
o.save('/tmp/logo/logo_full.png')
h=360;o2=o.resize((round(o.width*h/o.height),h),Image.LANCZOS);o2.save('/tmp/logo/logo.webp',quality=90,method=6)
bg=Image.new('RGBA',o.size,(6,19,58,255));bg.alpha_composite(o);bg.save('/tmp/logo/preview.png')
import os;print(o.size,os.path.getsize('/tmp/logo/logo.webp'))
