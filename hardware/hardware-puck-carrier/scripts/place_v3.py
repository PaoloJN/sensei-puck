import pcbnew, math, re, sys, json
PROJ='/Users/paolonessim/Projects/sensei-cup/hardware/hardware-puck-carrier'
PCB=PROJ+'/puck-carrier.kicad_pcb'; LIB=PROJ+'/lib/footprints/puck-parts.pretty'
b=pcbnew.LoadBoard(PCB)
mm=pcbnew.FromMM; tomm=pcbnew.ToMM
def P(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
CX,CY,R=150.0,100.0,23.0
def pol(r,a): return (CX+r*math.cos(math.radians(a)), CY-r*math.sin(math.radians(a)))
F,B=pcbnew.F_Cu,pcbnew.B_Cu
_IO=[]
def fpload(lib,name):
    try:
        io=pcbnew.PCB_IO_MGR.PluginFind(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    except Exception:
        io=pcbnew.PCB_IO_KICAD_SEXPR()
    _IO.append(io)
    f=io.FootprintLoad(lib,name); assert f, name; return f
_FPS={f.GetReference():f for f in b.GetFootprints()}
def fp(ref):
    f=_FPS.get(ref); assert f is not None, ref; return f

# (stale tracks/groups/guides stripped from the file beforehand)
# ---------- 2. relink footprint lib ids to the schematic's qualified names
sch=open(PROJ+'/puck-carrier.kicad_sch').read()
schfp={}
for m in re.finditer(r'\(property "Reference" "([^"]+)"(?:.*\n){0,40}?\s*\(property "Footprint" "([^"]*)"', sch):
    schfp.setdefault(m.group(1), m.group(2))
relinked=0
for f in b.GetFootprints():
    ref=f.GetReference(); want=schfp.get(ref)
    if not want: continue
    cur=f.GetFPIDAsString()
    if cur!=want and cur.split(':')[-1]==want.split(':')[-1]:
        f.SetFPIDAsString(want); relinked+=1
    elif cur!=want and ref=='U10':
        f.SetFPIDAsString(want); relinked+=1
print('relinked',relinked)

# ---------- 4. placement
def place(ref, x, y, rot=0, layer=F, anchor='origin'):
    f=fp(ref)
    if f.GetLayer()!=layer: f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot); f.SetPosition(P(x,y))
    if anchor=='bbox':
        c=f.GetCourtyard(pcbnew.F_CrtYd if layer==F else pcbnew.B_CrtYd).BBox().GetCenter()
        f.SetPosition(P(x-(tomm(c.x)-x), y-(tomm(c.y)-y)))
    return f
def placepol(ref,r,a,rot,layer=F):
    x,y=pol(r,a); place(ref,x,y,rot,layer)

# TOP ------------------------------------------------------------
ring=[('D%d'%(10+k), 37.5+21*k) for k in range(6)]+[('D%d'%(16+k), 217.5+21*k) for k in range(6)]
for ref,a in ring: placepol(ref,20.5,a,(a-90)%360)
for ref,a in zip(('C18','C19','C20','C21','C22','C23'),(48,90,132,228,270,312)): placepol(ref,18.6,a,(a-90)%360)
for ref,a in (('E3',24),('E1',8),('E2',-8),('E4',-24)): placepol(ref,16.5,a,(a+90)%360)
place('FDC1',148.4,100); place('FDC2',148.4,100)
place('U9',142.2,92.5,90); place('C11',142.2,89.0,0)
place('U5',142.2,107.5,0); place('C14',142.2,111.0,0)
place('U3',156.7,100,0); place('D1',157.3,93.5,0); place('D2',157.3,106.5,0); place('D3',159.7,100,90)
place('E5',146.4,91.0,0,F); place('E6',146.4,109.0,0,F)
place('U6',151.6,90.4,90,F)          # DS18B20U+ uSOP on the sensor face, on the axis

# BOTTOM ---------------------------------------------------------
u1=fp('U1'); u1.SetPosition(P(136.3,100.0))   # keep rot -90 / antenna west, pull inboard
# piezo block NW
place('Q5',134.6,87.8,0,B); place('PZ1',140.1,86.5,0,B)
for ref,x in (('R13',137.6),('R24',139.8),('R28',142.0)): place(ref,x,82.7,0,B)
# battery connector, pins THT at (145.5/147.5, 83.5), body toward board centre
j1=place('J1',146.0,82.5,0,B)
best=None
for rot in (0,90,180,270):
    j1.SetOrientationDegrees(rot); j1.SetPosition(P(146.0,82.5))
    c=j1.GetCourtyard(pcbnew.B_CrtYd).BBox(); cy=tomm(c.GetCenter().y); cx=tomm(c.GetCenter().x)
    pads=[(tomm(p.GetPosition().x),tomm(p.GetPosition().y)) for p in j1.Pads()]
    if all(abs(py-82.5)<0.01 for _,py in pads) and cy>83:
        best=rot
j1.SetOrientationDegrees(best if best is not None else 0); j1.SetPosition(P(146.0,82.5))
if min(tomm(p.GetPosition().x) for p in j1.Pads())<145.9: j1.SetPosition(P(148.0,82.5))
# SWD test points row
for k,ref in enumerate(('TP13','TP14','TP15','TP16','TP17')): place(ref,152.4+2.6*k,83.7,0,B)
# module support column
for ref,y,rot in (('C17',92.8,90),('C3',97.0,90)): place(ref,146.4,y,rot,B)
place('C12',149.2,90.8,0,B); place('C13',151.4,90.8,0,B); place('L2',153.4,87.7,90,B)
# centre column: FDC1004 + IMU
place('U4',150,94.5,90,B); place('C8',153,94.5,90,B); place('C16',153,97.6,90,B)
place('U8',150,101,0,B); place('C9',153,101,90,B); place('R14',147.0,90.8,0,B)
# boost NE
place('C5',157.5,86.6,0,B); place('U2',157.5,88.9,0,B); place('C6',157.5,91.2,0,B); place('L1',162.5,89.1,0,B)
place('R15',161,93.5,0,B); place('R16',163.2,93.5,0,B); place('D9',161.5,95.9,0,B); place('R32',167.8,96.4,0,B)
# EC front end E
for k,ref in enumerate(('R20','R21','R22','R23','R26','R27')): place(ref,155.5+2.2*k,98.6,0,B)
place('C1',157.5,101.1,0,B); place('C2',161.8,101.1,0,B)
for k,ref in enumerate(('R1','R2','R3','R4')): place(ref,155.5+2.2*k,103.6,0,B)
place('TP6',164.9,103.6,0,B); place('TP7',165.2,100.7,0,B)
for k,ref in enumerate(('TP21','TP22','TP23','TP24','TP25','TP26')): place(ref,168.8,99.3+2.0*k,90,B)
# charger S-centre
for k,ref in enumerate(('R29','R30','R17','R31')): place(ref,148.5+2.2*k,105.6,0,B)
place('U11',149.3,108.7,0,B); place('U7',154.3,108.7,0,B)
place('D6',151.3,112.5,0,B); place('D8',156.0,112.5,0,B); place('C10',158.8,112.5,90,B)
# LDO + FET bank SW
place('U10',144.4,111.7,0,B); place('C7',147.0,111.9,90,B); place('C15',148.2,111.9,90,B)
place('Q1',139.6,107.8,0,B); place('Q2',143.8,107.8,0,B); place('Q3',140.4,111.7,0,B)
for k,ref in enumerate(('R8','R9','R10','R5','R6','R7')): place(ref,138.3+2.2*k,114.8,0,B)
# thermal SE
place('R11',163.4,107.6,0,B); place('Q4',161.5,111.8,0,B); place('R12',165.5,112.2,0,B)
# dock
for k,ref in enumerate(('CP1','CP2','CP3','CP4')): place(ref,143.25+4.5*k,118.0,0,B)

for ref,x,y in (('FID1',154.5,117.0),('FID2',154.5,83.0),('FID3',147.6,86.6),('FID4',167.0,92.5),('FID5',136.5,112.3),('FID6',162.0,115.5),('FID7',147.6,113.4)):
    f=fp(ref); f.SetPosition(P(x,y))
# ---------- 6. antenna rule area (all copper layers, both faces)
z=pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName('ANTENNA_KEEPOUT')
z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowFootprints(True); z.SetDoNotAllowPads(False)
ls=pcbnew.LSET()
for l in (pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu): ls.addLayer(l)
z.SetLayerSet(ls)
o=z.Outline(); o.NewOutline()
for x,y in ((125.5,89.75),(137.3,89.75),(137.3,94.2),(127.9,94.2),(127.9,105.8),(137.3,105.8),(137.3,110.25),(125.5,110.25)): o.Append(mm(x),mm(y))
b.Add(z)

# ---------- 7. silkscreen: hide all refdes, add deliberate marks
for f in b.GetFootprints(): f.Reference().SetVisible(False)
def txt(s,x,y,layer,size=0.8,rot=0,thick=None):
    t=pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x,y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size),mm(size))); t.SetTextThickness(mm(thick or max(0.15,size*0.18)))
    t.SetTextAngleDegrees(rot); t.SetMirrored(layer==pcbnew.B_SilkS); b.Add(t)
FS,BS=pcbnew.F_SilkS,pcbnew.B_SilkS
txt('WATER PUCK',131.0,100,FS,1.5,90,0.25); txt('spin 1  ·  2026-09',133.4,100,FS,0.8,90)
txt('W',157.3,90.6,FS,0.8,90); txt('IR',157.3,109.4,FS,0.8,90); txt('UV',159.7,96.4,FS,0.8,90)
txt('SWD',157.6,80.6,BS,0.8)
for k,s in enumerate(('DIO','CLK','RST','VDD','GND')): txt(s,152.4+2.6*k,85.6 if s=='GND' else 81.9,BS,0.8,0,0.15)
for k,s in enumerate(('GND','D-','D+','5V')): txt(s,143.25+4.5*k,120.3,BS,0.8)
vb=[p for p in fp('J1').Pads() if p.GetNetname()=='VBAT']
txt('BAT',147.0,80.3,BS,0.8); 
if vb: txt('+',tomm(vb[0].GetPosition().x),84.5,BS,0.8)
txt('PZ',140.1,89.7,BS,0.8); txt('NFC',150.9,87.7,BS,0.8,90); 

def eco_circle(x,y,r):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(P(x,y)); s.SetEnd(P(x+r,y)); s.SetLayer(pcbnew.Eco1_User); s.SetWidth(mm(0.15)); b.Add(s)
def eco_poly(pts):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_POLY); ch=pcbnew.SHAPE_POLY_SET(); ch.NewOutline()
    for x,y in pts: ch.Append(mm(x),mm(y))
    s.SetPolyShape(ch); s.SetLayer(pcbnew.Eco1_User); s.SetWidth(mm(0.15)); s.SetFilled(False); b.Add(s)
eco_circle(146.4,91.0,2.3); eco_circle(146.4,109.0,2.3); eco_circle(142.2,107.5,2.4); eco_circle(142.2,92.5,1.6)
eco_poly([pol(11.3,a) for a in range(-30,31,5)]+[pol(21.7,a) for a in range(30,-31,-5)])
txt('DIP MASK: keep these areas free of epoxy (Eco1)',150,124.5,pcbnew.Eco1_User,1.0)
pcbnew.SaveBoard(PCB,b)
print('saved', b.GetFootprints().__len__(),'footprints')

# ---------- 8. checker
def bbox(f):
    c=f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer()==F else pcbnew.B_CrtYd).BBox()
    return (tomm(c.GetLeft()),tomm(c.GetTop()),tomm(c.GetRight()),tomm(c.GetBottom()))
fps=list(b.GetFootprints())
bad=0
for i,f1 in enumerate(fps):
    b1=bbox(f1)
    for f2 in fps[i+1:]:
        if f1.GetLayer()!=f2.GetLayer(): continue
        b2=bbox(f2)
        if b1[0]<b2[2] and b2[0]<b1[2] and b1[1]<b2[3] and b2[1]<b1[3]:
            ox=min(b1[2],b2[2])-max(b1[0],b2[0]); oy=min(b1[3],b2[3])-max(b1[1],b2[1])
            print('OVERLAP %s %s  %.2f x %.2f'%(f1.GetReference(),f2.GetReference(),ox,oy)); bad+=1
for f in fps:
    l,t,r,bt=bbox(f)
    for x,y in ((l,t),(r,t),(l,bt),(r,bt)):
        rr=math.hypot(x-CX,y-CY)
        if rr>22.55 and f.GetReference()!='U1': print('RIM %s corner r=%.2f'%(f.GetReference(),rr)); bad+=1; break
# THT pads vs other-face courtyards
tht=[(f.GetReference(),p) for f in fps for p in f.Pads() if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH]
for ref,p in tht:
    px,py=tomm(p.GetPosition().x),tomm(p.GetPosition().y); pr=tomm(p.GetSizeX())/2
    for f in fps:
        if f.GetReference()==ref: continue
        l,t,r,bt=bbox(f)
        dx=max(l-px,0,px-r); dy=max(t-py,0,py-bt); d=math.hypot(dx,dy)-pr
        if d<0.3: print('THT %s pad %s near %s (%s) gap %.2f'%(ref,p.GetNumber(),f.GetReference(),f.GetLayerName(),d)); bad+=1
# antenna polygon membership (courtyards) for anything but U1
poly=[(125.5,89.75),(137.3,89.75),(137.3,94.2),(127.9,94.2),(127.9,105.8),(137.3,105.8),(137.3,110.25),(125.5,110.25)]
def inpoly(x,y):
    n=len(poly); inside=False
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: inside=not inside
    return inside
for f in fps:
    if f.GetReference()=='U1': continue
    l,t,r,bt=bbox(f)
    if any(inpoly(x,y) for x,y in ((l,t),(r,t),(l,bt),(r,bt),((l+r)/2,(t+bt)/2))): print('KEEPOUT',f.GetReference()); bad+=1
print('U6 pins', [(round(tomm(p.GetPosition().x),2),round(tomm(p.GetPosition().y),2)) for p in fp('U6').Pads()], 'J1 rot',fp('J1').GetOrientationDegrees(), 'J1 bbox',[round(v,2) for v in bbox(fp('J1'))], 'U6 bbox',[round(v,2) for v in bbox(fp('U6'))])
print('violations',bad)
