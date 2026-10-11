# route_pre.py <in.kicad_pcb> <out.kicad_pcb> — scripted pre-route for hand routing handoff
import pcbnew, math, sys
IN,OUT=sys.argv[1:3]
mm=pcbnew.FromMM; tomm=pcbnew.ToMM; CX,CY=150.0,100.0
b=pcbnew.LoadBoard(IN)
F,B=pcbnew.F_Cu,pcbnew.B_Cu
def P(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
def pol(r,a): return (CX+r*math.cos(math.radians(a)), CY-r*math.sin(math.radians(a)))
_FPS={f.GetReference():f for f in b.GetFootprints()}
def fp(r): return _FPS[r]
def pad(ref,num):
    for p in fp(ref).Pads():
        if p.GetNumber()==str(num): return p
    raise KeyError((ref,num))
def padxy(ref,num): p=pad(ref,num); return (tomm(p.GetPosition().x),tomm(p.GetPosition().y))
def net(name): n=b.FindNet(name); assert n,name; return n
def track(pts,w,layer,netname):
    n=net(netname)
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
        if abs(x1-x2)<1e-6 and abs(y1-y2)<1e-6: continue
        t=pcbnew.PCB_TRACK(b); t.SetStart(P(x1,y1)); t.SetEnd(P(x2,y2)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(n); b.Add(t)
def via(x,y,netname,d=0.6,drill=0.3):
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(x,y)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetDrill(mm(drill)); v.SetWidth(mm(d)); v.SetLayerPair(F,B); v.SetNet(net(netname)); b.Add(v)
def place(ref,x,y,rot,layer=None):
    f=fp(ref)
    if layer is not None and f.GetLayer()!=layer: f.Flip(f.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot); f.SetPosition(P(x,y))
def arc(r,a0,a1,step=3.0):
    n=max(1,int(abs(a1-a0)/step)); return [pol(r,a0+(a1-a0)*i/n) for i in range(n+1)]

# ---------- placement tweaks for routability
place('L1',162.5,89.1,180)          # SW pad faces U2
place('C6',157.5,91.2,180)          # 5V pad on the U2 side
place('R14',146.4,90.5,0); place('C12',148.6,90.5,0); place('C13',153.4,91.5,0)
place('R32',144.2,90.8,0)           # ring data series R next to the module escape vias
ring=[('D%d'%(10+k), 142.5-21*k) for k in range(6)]+[('D%d'%(16+k), 322.5-21*k) for k in range(6)]
for ref,a in ring:
    x,y=pol(20.5,a); place(ref,x,y,(a+90)%360)   # VDD/DOUT inner, GND/DIN outer, chain runs clockwise

# ---------- boost hot loop (B.Cu, 0.5 mm)
p5=padxy('U2',5); track([p5,(p5[0]+0.55,p5[1])],0.25,B,'/BOOST_SW'); track([(p5[0]+0.55,p5[1]),(159.1,p5[1]),padxy('L1',2)],0.5,B,'/BOOST_SW')
x3,y3=padxy('U2',3); x5,y5=padxy('C5',1)
track([(x3,y3),(x5,y5)],0.3,B,'VBAT')
lx,ly=padxy('L1',1)
track([(lx,ly),(lx,85.3),(x5,85.3),(x5,y5)],0.5,B,'VBAT')
p6=padxy('U2',6); track([p6,(p6[0],p6[1]+0.55)],0.25,B,'5V'); track([(p6[0],p6[1]+0.55),padxy('C6',1)],0.5,B,'5V')
track([padxy('R15',2),(162.1,93.5),padxy('R16',1)],0.2,B,'/BOOST_FB')
# 5V_RING: D9 -> via -> top bus (FB / 5V->R15 / 5V->D9 left for hand routing)
track([padxy('D9',1),(158.9,95.9)],0.4,B,'/5V_RING'); via(158.9,95.9,'/5V_RING',0.8,0.4)
track([(158.9,95.9),(160.0,95.9),(160.0,87.4),pol(19.5,55)],0.5,F,'/5V_RING')

# ---------- LED ring (F.Cu)
BUS=19.5
bus=arc(BUS,144.0,33.0)+[pol(21.5,30.0)]+arc(21.5,30.0,-30.0)+[pol(BUS,-33.0)]+arc(BUS,-33.0,-141.5)
track(bus,0.5,F,'/5V_RING')
for ref,a in ring:
    x,y=padxy(ref,2); r=math.hypot(x-CX,y-CY); ang=math.degrees(math.atan2(-(y-CY),x-CX))
    track([(x,y),pol(BUS+0.1,ang)],0.25,F,'/5V_RING')
for ref,a in (('C18',48),('C19',90),('C20',132),('C21',228),('C22',270),('C23',312)):
    x,y=padxy(ref,1); ang=math.degrees(math.atan2(-(y-CY),x-CX))
    track([(x,y),pol(BUS-0.1,ang)],0.25,F,'/5V_RING')
# data chain (clockwise): DOUT(n) inner CW -> DIN(n+1) outer CCW
def ang_of(x,y): return math.degrees(math.atan2(-(y-CY),x-CX))
for k in range(len(ring)-1):
    r1,a1=ring[k]; r2,a2=ring[k+1]
    do=padxy(r1,1); di=padxy(r2,4); nn=pad(r1,1).GetNetname()
    if k==5:   # east gap hop, outside the electrode tips
        pts=[do,pol(20.15,ang_of(*do)-1.0),pol(21.8,32.0),pol(21.8,0),pol(21.8,-32.0),pol(21.8,ang_of(*di)+2.5),di]
        pts=[do,pol(20.15,ang_of(*do)-2.6),pol(22.05,ang_of(*do)-3.6)]+arc(22.05,ang_of(*do)-3.6,ang_of(*di)+1.8,3)+[pol(20.9,ang_of(*di)+1.0),di]
    else:
        a_do=ang_of(*do); a_di=ang_of(*di)
        pts=[do,pol(20.15,a_do-0.8)]+arc(20.15,a_do-0.8,a_di+4.0,2)+[pol(20.9,a_di+2.2),di]
    track(pts,0.25,F,nn)
# RING_DATA input: R32 -> bottom west under J1 -> via -> top, approaching D10 DIN from outside
rx,ry=padxy('R32',2); track([(rx,ry),(rx,89.4),(136.6,89.4)],0.25,B,'/RING_D0'); via(136.6,89.4,'/RING_D0')
d10=padxy('D10',4)
track([(136.6,89.4),(134.3,89.4),(132.3,88.6),d10],0.25,F,'/RING_D0')

# ---------- electrode stubs + vias (F.Cu, 0.25)
for ref,vx,vy in (('E3',160.8,94.9),('E1',162.0,99.6),('E2',162.0,102.55),('E4',160.8,105.1)):
    p=pad(ref,1); nn=p.GetNetname(); cx,cy=padxy(ref,1); a=ang_of(cx,cy)
    inner=pol(12.6,a)   # pad inner end
    track([inner,(vx,vy)],0.25,F,nn); via(vx,vy,nn)
# ---------- FDC sense pads: vias inside the (mask-covered) pads, stubs to U4
via(150.5,98.2,'/CIN1'); track([(150.5,98.2),padxy('U4',2)],0.2,B,'/CIN1')
via(154.5,97.0,'SHLD1'); track([padxy('U4',1),(151.0,93.45),(155.9,93.45),(155.9,97.0),(154.5,97.0)],0.2,B,'SHLD1')
c2=padxy('U4',3)
track([c2,(c2[0],97.9),(148.0,97.9),(148.0,99.9),(146.3,99.9),(146.3,105.0)],0.2,B,'/CIN2'); via(146.3,105.0,'/CIN2')

# ---------- GND stitching vias
poly=[(125.5,89.75),(137.3,89.75),(137.3,93.6),(127.9,93.6),(127.9,106.5),(137.3,106.5),(137.3,110.25),(125.5,110.25)]
def inpoly(x,y):
    n=len(poly); inside=False
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: inside=not inside
    return inside
pads=[(tomm(p.GetPosition().x),tomm(p.GetPosition().y),max(tomm(p.GetSizeX()),tomm(p.GetSizeY()))/2) for f in b.GetFootprints() for p in f.Pads()]
segs=[t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK']; vias=[t for t in b.GetTracks() if t.GetClass()=='PCB_VIA']
def segdist(x,y,t):
    x1,y1,x2,y2=tomm(t.GetStart().x),tomm(t.GetStart().y),tomm(t.GetEnd().x),tomm(t.GetEnd().y)
    dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy; u=0 if L==0 else max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L))
    return math.hypot(x-(x1+u*dx),y-(y1+u*dy))-tomm(t.GetWidth())/2
added=0
for gx in range(-6,7):
    for gy in range(-7,8):
        x,y=CX+gx*3.5+(1.75 if gy%2 else 0),CY+gy*3.0
        r=math.hypot(x-CX,y-CY); a=ang_of(x,y)
        if r>21.0 or inpoly(x,y): continue
        if r>10 and -33<a<33: continue
        if math.hypot(x-148.4,y-100)<7.8: continue
        if any(math.hypot(x-tomm(f.GetPosition().x),y-tomm(f.GetPosition().y))<2.0 for f in b.GetFootprints() if f.GetReference().startswith('FID')): continue
        if x<144.8 and 93.6<y<106.5: continue
        if any(math.hypot(x-px,y-py)<pr+0.75 for px,py,pr in pads): continue
        if any(segdist(x,y,t)<0.55 for t in segs): continue
        if any(math.hypot(x-tomm(v.GetPosition().x),y-tomm(v.GetPosition().y))<1.0 for v in vias): continue
        via(x,y,'GND'); added+=1
print('stitch vias',added)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT,b); print('saved',OUT, 'tracks',len([t for t in b.GetTracks()]))
