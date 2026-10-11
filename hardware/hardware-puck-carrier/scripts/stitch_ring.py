"""Add radial GND returns outside the LED data chain; requires KiCad Python.
Usage: stitch_ring.py input.kicad_pcb output.kicad_pcb. Run DRC after use.
"""
import math,sys,pcbnew
b=pcbnew.LoadBoard(sys.argv[1]);mm=pcbnew.FromMM
for ref in (f'D{i}' for i in range(10,22)):
 f=b.FindFootprintByReference(ref)
 p=next(p for p in f.Pads() if p.GetNetname()=='GND')
 x,y=pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)
 r=math.hypot(x-150,y-100);vx,vy=150+(x-150)*21.8/r,100+(y-100)*21.8/r
 end=pcbnew.VECTOR2I(mm(vx),mm(vy))
 if any(t.GetClass()=='PCB_VIA' and (t.GetPosition()-end).EuclideanNorm()<mm(.01) for t in b.GetTracks()):continue
 t=pcbnew.PCB_TRACK(b);t.SetStart(p.GetPosition());t.SetEnd(end);t.SetWidth(mm(.2));t.SetLayer(pcbnew.F_Cu);t.SetNet(p.GetNet());b.Add(t)
 v=pcbnew.PCB_VIA(b);v.SetPosition(end);v.SetViaType(pcbnew.VIATYPE_THROUGH);v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetNet(p.GetNet());b.Add(v)
filler=pcbnew.ZONE_FILLER(b);filler.Fill(b.Zones());pcbnew.SaveBoard(sys.argv[2],b)
