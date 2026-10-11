"""Hand-routed segments that the fan-out search and the autorouter cannot do.

KiCad Python: route_manual.py input.kicad_pcb output.kicad_pcb

The FDC1/FDC2 sense pads on F.Cu forbid any foreign via inside r ~6.45 mm of
(148.4, 100), so everything under them is routed on B.Cu to vias outside
that circle:
  * /CIN2 (FDC2 ring sense) is moved from the west side of U8 to the east
    side, so the west bay is free for the IMU's 3V3 pin.
  * U8 3V3 pins: pad 5 -> C3 pad 1 (west), pads 8 and 12 -> C9 pad 1 (east;
    C9 has a plane via).
  * U1-28 (module 3V3) -> trunk up the corridor between the module and C3 ->
    C3 pad 1 and C17 pad 1 (plane via).
  * U4-8 (FDC1004 3V3) and U4-7 (GND) get staggered vias north of the part
    where the GND_BOT pull-back cannot reach.
Coordinates in mm, board frame. Run DRC after use.
"""
import sys, pcbnew
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'wiring'))
from sexp import parse, find, find_all, atom, serialize
IN, OUT = sys.argv[1:3]

def drop_net_textually(src, dst, names):
    """Removing tracks through the SWIG API crashes KiCad 10; strip them in the file instead."""
    doc = parse(Path(src).read_text())[0]
    for item in [i for i in doc if isinstance(i, list) and i and atom(i[0]) in ('segment', 'via', 'arc')]:
        n = find(item, 'net')            # KiCad 10 stores the net by name on tracks
        if n and atom(n[1]) in names: doc.remove(item)
    Path(dst).write_text(serialize(doc) + '\n')

TMP = OUT + '.stripped.kicad_pcb'
drop_net_textually(IN, TMP, {'/CIN2'})
b = pcbnew.LoadBoard(TMP)
mm = pcbnew.FromMM
B = pcbnew.B_Cu
def P(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))
def net(n): r = b.FindNet(n); assert r, n; return r
def track(pts, w, layer, n):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net(n)); b.Add(t)
def via(x, y, n, d=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetDrill(mm(drill)); v.SetWidth(mm(d))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net(n)); b.Add(v)
# --- /CIN2: U4 pad 3 south, under the CIN1 via, east to the FDC2 ring
track([(150.0, 96.65), (150.0, 97.3), (149.92, 97.5), (149.92, 98.9), (153.6, 98.9), (153.6, 99.2)], 0.2, B, '/CIN2')   # jog west to clear the CIN1 via
via(153.6, 99.2, '/CIN2')

# --- 3V3 trunk: U1-28 -> corridor x=144.3 -> C3 pad 1 (y 98.56) and C17 pad 1 (y 93.28)
track([(143.45, 101.6), (144.3, 101.6), (144.3, 93.28), (146.4, 93.28)], 0.3, B, '3V3')
track([(144.3, 98.56), (148.3, 98.56), (148.3, 99.3), (149.5, 99.3), (149.5, 100.09)], 0.3, B, '3V3')   # through C3 pad 1 on to U8 pad 5

# --- U8 pads 8 and 12 -> C9 pad 1
track([(151.16, 100.25), (152.2, 100.25), (152.2, 101.48), (153.0, 101.48)], 0.3, B, '3V3')
track([(150.5, 101.91), (150.5, 102.5), (152.6, 102.5), (152.6, 101.48)], 0.3, B, '3V3')

# --- U4 north row: 3V3 (pad 8) and GND (pad 7) vias, staggered
track([(150.0, 92.35), (150.0, 90.9)], 0.3, B, '3V3'); via(150.0, 90.9, '3V3')
track([(149.5, 92.35), (149.5, 91.3), (149.1, 90.9)], 0.3, B, 'GND'); via(149.1, 90.9, 'GND')

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT, b); Path(TMP).unlink(); print('saved', OUT)
