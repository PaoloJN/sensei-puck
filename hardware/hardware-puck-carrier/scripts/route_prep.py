# prep_route.py — routing prep for puck-carrier: net classes, planes, pull-backs, DSN export.
import pcbnew, math, json, sys
PROJ='/Users/paolonessim/Projects/sensei-cup/hardware/hardware-puck-carrier'
PCB=PROJ+'/puck-carrier.kicad_pcb'; OUT=sys.argv[1] if len(sys.argv)>1 else PCB
mm=pcbnew.FromMM; CX,CY=150.0,100.0
def P(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
# ---- net classes (project file)
pj=PROJ+'/puck-carrier.kicad_pro'; d=json.load(open(pj))
base=d['net_settings']['classes'][0]
def cls(name,clr,tw,vd,vdr,prio,**kw):
    c=dict(base); c.update({'name':name,'clearance':clr,'track_width':tw,'via_diameter':vd,'via_drill':vdr,'priority':prio}); c.update(kw); return c
d['net_settings']['classes']=[
 cls('Default',0.15,0.2,0.6,0.3,2147483647),
 cls('power',0.15,0.4,0.8,0.4,3),
 cls('boost',0.15,0.5,0.8,0.4,0),
 cls('ec',0.2,0.25,0.6,0.3,1),
 cls('usb',0.15,0.2,0.6,0.3,2,diff_pair_width=0.2,diff_pair_gap=0.15),
 cls('ring',0.15,0.25,0.6,0.3,4),
 cls('led',0.15,0.35,0.6,0.3,5),
]
pat=[('power',p) for p in ('GND','3V3','VBAT','VBUS','*PAD_5V','1V8')]
pat+=[('boost',p) for p in ('5V','*BOOST_SW','*5V_RING')]
pat+=[('ec',p) for p in ('EC_*','*EC_NODE_D','EC_BIAS','EXP_A4','EXP_A5')]
pat+=[('usb',p) for p in ('*PAD_DP','*PAD_DM','USB_DP','USB_DM')]
pat+=[('ring',p) for p in ('*RING_D*','RING_DATA')]
pat+=[('led',p) for p in ('*LED?_A','*LED?_K','*HTR_SW','*PZ_DRV')]
d['net_settings']['netclass_patterns']=[{'netclass':n,'pattern':p} for n,p in pat]
r=d['board']['design_settings']['rules']; r['min_clearance']=0.15; r['min_track_width']=0.15; r['min_via_diameter']=0.5; r['min_via_annular_width']=0.1; r['min_copper_edge_clearance']=0.5
d['board']['design_settings'].setdefault('rule_severities',{})['starved_thermal']='warning'; d['board']['design_settings']['rule_severities']['missing_courtyard']='ignore'
json.dump(d,open(pj,'w'),indent=2); print('netclasses written')

b=pcbnew.LoadBoard(PCB)
# ---- drop stale single-pad UVC nets on U1
for p in b.FindFootprintByReference('U1').Pads():
    if p.GetNetname() in ('UVC_PD','UVC_EN'): p.SetNetCode(0)
# ---- zones
def circle(cx,cy,r,n=72,a0=0,a1=360):
    pts=[]; span=a1-a0
    for i in range(n+1 if span<360 else n):
        a=math.radians(a0+span*i/n); pts.append((cx+r*math.cos(a), cy-r*math.sin(a)))
    return pts
def sector(r0,r1,a0,a1,n=24):
    return circle(CX,CY,r1,n,a0,a1)+list(reversed(circle(CX,CY,r0,n,a0,a1)))
def zone(name,layer,pts,net=None,prio=0,keep=None,clearance=0.25):
    z=pcbnew.ZONE(b); z.SetZoneName(name)
    if keep:
        z.SetIsRuleArea(True); z.SetDoNotAllowZoneFills('fills' in keep); z.SetDoNotAllowTracks('tracks' in keep); z.SetDoNotAllowVias('vias' in keep); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowPads(False)
        ls=pcbnew.LSET()
        for l in (layer if isinstance(layer,(list,tuple)) else [layer]): ls.addLayer(l)
        z.SetLayerSet(ls)
    else:
        z.SetLayer(layer); z.SetNet(b.FindNet(net)); z.SetAssignedPriority(prio)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(clearance))
        z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.25)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    o=z.Outline(); o.NewOutline()
    for x,y in pts: o.Append(mm(x),mm(y))
    b.Add(z); return z
full=circle(CX,CY,22.4)
zone('GND_IN1',pcbnew.In1_Cu,full,'GND',0)
zone('PWR_3V3_IN2',pcbnew.In2_Cu,full,'3V3',0)
zone('GND_TOP',pcbnew.F_Cu,full,'GND',0,clearance=0.3)
zone('GND_BOT',pcbnew.B_Cu,full,'GND',0,clearance=0.3)
zone('SHLD1_FDC',pcbnew.In1_Cu,circle(148.4,100,6.9),'SHLD1',2)
# pull-backs
ec=sector(10.5,22.6,-32,32)
zone('KO_EC_PLANES',[pcbnew.In1_Cu,pcbnew.In2_Cu],ec,keep=('fills','tracks'))
zone('KO_EC_TOPFILL',pcbnew.F_Cu,ec,keep=('fills',))
for nm,(x,y) in (('FDC',(148.4,100)),):
    zone('KO_%s_IN2'%nm,pcbnew.In2_Cu,circle(x,y,6.7),keep=('fills','tracks'))
    zone('KO_%s_TOP'%nm,pcbnew.F_Cu,circle(x,y,6.7),keep=('fills',))
for nm,(x,y) in (('E5',(146.4,91.0)),('E6',(146.4,109.0))):
    zone('KO_%s_TOP'%nm,pcbnew.F_Cu,circle(x,y,2.6,24),keep=('fills',))
# rim keep-out (edge clearance 0.5) + fiducial track keep-outs
rim=circle(CX,CY,23.6,72)+list(reversed(circle(CX,CY,22.35,72)))
zone('KO_RIM',[pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu],rim,keep=('tracks','vias'))
for f in b.GetFootprints():
    if f.GetReference().startswith('FID'):
        x,y=pcbnew.ToMM(f.GetPosition().x),pcbnew.ToMM(f.GetPosition().y)
        zone('KO_'+f.GetReference(),f.GetLayer(),circle(x,y,1.4,20),keep=('tracks','vias'))
# module escape stubs + vias for inner-row pads (0.6x0.4 pads at 0.8 pitch cannot exit sideways)
u1=b.FindFootprintByReference('U1'); tomm=pcbnew.ToMM; nesc=0
def via_stub(pad,vx,vy,w=0.2):
    global nesc
    net=pad.GetNet(); px,py=tomm(pad.GetPosition().x),tomm(pad.GetPosition().y)
    t=pcbnew.PCB_TRACK(b); t.SetStart(P(px,py)); t.SetEnd(P(vx,vy)); t.SetWidth(mm(w)); t.SetLayer(pcbnew.B_Cu); t.SetNet(net); b.Add(t)
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(vx,vy)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetDrill(mm(0.3)); v.SetWidth(mm(0.6)); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetNet(net); b.Add(v); nesc+=1
for pad in u1.Pads():
    n=pad.GetNetname()
    if not n or 'unconnected' in n or n in ('UART_TX','UART_RX'): continue
    x,y=round(tomm(pad.GetPosition().x),2),round(tomm(pad.GetPosition().y),2)
    w=0.25 if n.startswith('EC_') else 0.2
    if abs(y-103.75)<0.05: via_stub(pad,x,102.85,w)          # south inner row -> north
    elif abs(y-96.25)<0.05: via_stub(pad,x,97.15,w)          # north inner row -> south
    elif abs(x-142.55)<0.05: via_stub(pad,141.65,y,w)        # east inner column -> west
    elif abs(x-136.85)<0.05 and 97.9<y<102.1: via_stub(pad,137.75,y,w)   # interior pads -> east
    elif abs(y-104.65)<0.05 and n=='GND' and x<133: via_stub(pad,133.0,105.55)
    elif abs(y-95.35)<0.05 and n=='GND' and 133<x<134: via_stub(pad,x,94.45)
print('module escapes',nesc)
for z in b.Zones():
    if z.GetZoneName()=='ANTENNA_KEEPOUT':
        o=z.Outline(); o.RemoveAllContours(); o.NewOutline()
        for x,y in ((125.5,89.75),(137.3,89.75),(137.3,93.6),(127.9,93.6),(127.9,106.5),(137.3,106.5),(137.3,110.25),(125.5,110.25)): o.Append(mm(x),mm(y))
pcbnew.SaveBoard(OUT,b); print('zones added, saved',OUT)
ok=pcbnew.ExportSpecctraDSN(b, OUT.replace('.kicad_pcb','.dsn')); print('dsn export',ok)
