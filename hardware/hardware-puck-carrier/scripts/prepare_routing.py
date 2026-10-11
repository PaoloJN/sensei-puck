"""Create module fan-out on an unrouted board, preserving existing planes.

KiCad Python: prepare_routing.py input.kicad_pcb output.kicad_pcb
Refuses to erase existing routing. Follow with route_pre.py and DRC.
"""
import sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
assert not list(b.GetTracks()), 'Input already has routes; refusing to overwrite them'
mm, tomm = pcbnew.FromMM, pcbnew.ToMM
def P(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))

def stub(p,x,y,w=0.2):
    t=pcbnew.PCB_TRACK(b);t.SetStart(p.GetPosition());t.SetEnd(P(x,y))
    t.SetWidth(mm(w));t.SetLayer(pcbnew.B_Cu);t.SetNet(p.GetNet());b.Add(t)
    v=pcbnew.PCB_VIA(b);v.SetPosition(P(x,y));v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetDrill(mm(0.3));v.SetWidth(mm(0.6));v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetNet(p.GetNet());b.Add(v)

for p in b.FindFootprintByReference('U1').Pads():
    n=p.GetNetname()
    if not n or n.startswith('unconnected') or n in ('UART_TX','UART_RX'): continue
    x,y=round(tomm(p.GetPosition().x),2),round(tomm(p.GetPosition().y),2)
    w=0.25 if n.startswith('EC_') else 0.2
    if abs(y-103.75)<0.05: stub(p,x,102.85,w)
    elif abs(y-96.25)<0.05: stub(p,x,97.15,w)
    elif abs(x-142.55)<0.05: stub(p,141.65,y,w)
    elif abs(x-136.85)<0.05 and 97.9<y<102.1: stub(p,137.75,y,w)
    elif abs(y-104.65)<0.05 and n=='GND' and x<133: stub(p,133.0,105.55)
    elif abs(y-95.35)<0.05 and n=='GND' and 133<x<134: stub(p,x,94.45)
for z in b.Zones():
    if z.GetZoneName()=='ANTENNA_KEEPOUT':
        o=z.Outline();o.RemoveAllContours();o.NewOutline()
        for x,y in ((125.5,89.75),(137.3,89.75),(137.3,93.6),(127.9,93.6),(127.9,106.5),(137.3,106.5),(137.3,110.25),(125.5,110.25)):o.Append(mm(x),mm(y))
pcbnew.SaveBoard(sys.argv[2],b)
