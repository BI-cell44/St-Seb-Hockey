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
QE=[(-1.49e-03,5.2974e-01,335.96244),(-1.29e-03,4.2534e-01,358.99266),(-1.19e-03,3.6613e-01,382.2906),(-1.19e-03,3.6881e-01,390.09112)]
def edge(i,y):
    a,b,c=QE[i]
    if y>=186: return a*y*y+b*y+c
    y0=186;return a*y0*y0+b*y0+c+(2*a*y0+b)*(y-y0)
def rlayer(x,y):
    return 4 if x<edge(0,y) else 3 if x<edge(1,y) else 2 if x<edge(2,y) else 1 if x<edge(3,y) else 0
def layer(x,y):
    d=y-(118+0.55*(x-304))
    lt=4 if d>=10 else 3 if d>=0 else 2 if d>=-18 else 1 if d>=-30 else 0
    lr=rlayer(x,y)
    return min(lt,lr)
_LEFT={}
def leftcol(y):
    if y not in _LEFT:
        cs=[src[x,yy] for yy in range(max(0,y-6),min(H,y+7)) for x in range(282,293) if src[x,yy][2]>120 and src[x,yy][0]<60 and src[x,yy][1]<90]
        _LEFT[y]=tuple(sum(c[i] for c in cs)/len(cs) for i in range(3)) if len(cs)>20 else INT
    return _LEFT[y]
def intcol(x,y):
    c=leftcol(y)
    t=min(1,max(0,(x-293)/40));return tuple(round(c[i]*(1-t)+INT[i]*t) for i in range(3))
def sub_top(x,y):
    ri=math.hypot(x-220.6,y-88.7);ro=math.hypot(x-221.2,y-89.5)
    if ri<=77: return None
    if ro<=85.4: return BL
    if ro<=88.5 and layer(x,y)<3: return WH
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
for y in range(0,201):
    for x in range(293,W):
        if 255<=x<330 and y>=173+0.0177*(x-288)**2-3 and sum(src[x,y])>660: continue
        if y>190: continue
        S(x,y,aa(sub_top,x,y,src[x,y]))
def sub_side(x,y):
    l=rlayer(x,y)
    if l==4: return None
    return COL[l]
for y in range(186,280):
    for x in range(340,W):
        if x<edge(0,y)-3: continue
        c=aa(sub_side,x,y,src[x,y])
        if y>=268:
            t=(y-268)/11;o=src[x,y];c=tuple(round(c[q]*(1-t)+o[q]*t) for q in range(3))
        S(x,y,c)
HC=[3.0313057577023543e-06,-0.003490761959377561,1.5208397946521053,-297.14919107036974,22141.43079004185]
for x in range(262,329):
    yt=float(np.polyval(HC,x));blue=P(x,int(yt)-7)
    for y in range(int(yt)-4,int(yt)+5):
        cov=min(1,max(0,(y+1)-yt))
        S(x,y,tuple(round(WH[q]*cov+blue[q]*(1-cov)) for q in range(3)))
# ---- bas du bouclier (géométrie) ----
kL,bL=1.0907,-337.9; kR,bR=-1.0924,779.0; TX,TY,CK=220,485,2.2
nL=math.sqrt(1+kL*kL);nR=math.sqrt(1+kR*kR);nC=math.sqrt(1+1/CK**2)
def dist(x,y):
    dl=(x-(kL*y+bL))/nL; dr=((kR*y+bR)-x)/nR
    dc=(TY-abs(x-TX)/CK-y)/nC
    return min(dl,dr,dc)
def stick(x,y):
    l1=176-(y-396)*0.167-0.5; r1=189.5-(y-396)*0.29
    l2=250-0.5+(y-396)*0.286; r2=261.5+(y-396)*0.155
    return min(max(l1-x,x-r1),max(l2-x,x-r2))
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
Y0,Y1=418,446
from PIL import ImageDraw
SC=4
def bez(p0,p1,p2,n=60):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/n for i in range(n+1)]]
Lx=lambda y:kL*y+bL; Rx=lambda y:kR*y+bR
TIP=(220,492)
poly=[(Lx(380),380),(Lx(430),430)]+bez((Lx(430),430),(Lx(485),485),TIP)[1:]+bez(TIP,(Rx(485),485),(Rx(430),430))[1:]+[(Rx(380),380)]
Hh=H2*SC;Ww=W*SC
mimg=Image.new('L',(Ww,Hh),0);ImageDraw.Draw(mimg).polygon([(x*SC,y*SC) for x,y in poly],fill=1)
mask=np.asarray(mimg).astype(bool)
y0=(Y0-2)*SC
sub=mask[y0:]
d=ndimage.distance_transform_edt(sub)/SC
yy,xx=np.mgrid[y0:Hh,0:Ww].astype(float);X=(xx+0.5)/SC;Yy=(yy+0.5)/SC
st=np.minimum(np.maximum((176-(Yy-396)*0.167-0.5)-X,X-(189.5-(Yy-396)*0.29)),np.maximum((249.5+(Yy-396)*0.286)-X,X-(261.5+(Yy-396)*0.155)))
BLB=np.array((5,42,205));ORB=np.array((249,102,12));WHa=np.array(WH);INa=np.array(INTB);BGa=np.array(BG)
C=np.empty(d.shape+(3,));C[:]=INa
C[d<30.5]=ORB
C[d<22.5]=WHa
C[(st<5.5)&(d>=10.5)]=BLB
C[(st<0)&(d>=9)]=WHa
C[d<9]=BLB
C[~sub]=BGa
lo=C.reshape(C.shape[0]//SC,SC,C.shape[1]//SC,SC,3).mean((1,3))
for y in range(Y0,H2):
    for x in range(W):
        c=tuple(int(round(v)) for v in lo[y-(Y0-2),x])
        between=(176-(y-396)*0.167-11)<=x<=(261.5+(y-396)*0.155+11)
        if y<=Y1 and not between:
            t=min(1,max(0,(y-434)/(Y1-434)));o=P(x,y);c=tuple(round(o[q]*(1-t)+c[q]*t) for q in range(3))
        S(x,y,c)
def sub_st(x,y):
    v=stick(x,y)
    if v<0: return WH
    if v<5.5: return BLB
    return None
for y in range(397,Y0):
    for x in range(150,280):
        if stick(x+0.5,y+0.5)>7: continue
        o=P(x,y);c=aa(sub_st,x,y,o)
        if y<402:
            t=(y-397)/5;c=tuple(round(o[q]*(1-t)+c[q]*t) for q in range(3))
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
