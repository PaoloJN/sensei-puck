"""Generate routes/5v-ring.json: the 5V LED ring as rounded arcs on F.Cu, plus the moves that clear its lane.

KICAD_PY gen_5v_ring.py board.kicad_pcb   (reads pad/via positions, writes 5v-ring.json beside this file)
Ring: r 19.45 between the caps (r 18.61) and the LEDs (r 20.1), C-shaped around the antenna keepout on the
west; crosses the EC finger sector on the east at r 22.0 (outside the finger tips); fed from D9.1 (B.Cu)
through one via on the east crossing. Radial stubs to every LED pad 2 and cap pad 1.
"""
import sys, math, json, pcbnew
from pathlib import Path
b = pcbnew.LoadBoard(sys.argv[1]); tomm = pcbnew.ToMM
CX, CY = 150.0, 100.0
R_RING, R_EAST, W = 19.45, 22.0, 0.5
def pt(r, a): return [round(CX + r * math.cos(math.radians(a)), 3), round(CY + r * math.sin(math.radians(a)), 3)]
def arc(r, a0, a1): return [*pt(r, a0), *pt(r, (a0 + a1) / 2), *pt(r, a1)]
def ang(x, y): return math.degrees(math.atan2(y - CY, x - CX))
def rad(x, y): return math.hypot(x - CX, y - CY)
pads = {}
for f in b.GetFootprints():
    for p in f.Pads(): pads[f'{f.GetReference()}.{p.GetNumber()}'] = (tomm(p.GetPosition().x), tomm(p.GetPosition().y), p.GetNetname())
def via_near(x, y, net, tol=0.6):
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA' and t.GetNetname() == net and math.hypot(tomm(t.GetPosition().x) - x, tomm(t.GetPosition().y) - y) < tol:
            return (round(tomm(t.GetPosition().x), 3), round(tomm(t.GetPosition().y), 3))
    raise SystemExit(f'no {net} via near {x},{y}')
d16_gnd_via = via_near(166.65, 114.22, 'GND')
spec = []
# ---- moves that clear the lane r 19.2-19.8 (each: remove old stub+via, add new stub+via)
spec += [
 {"name": "move Q5.2 GND via out of the ring lane", "net": "GND", "layer": "B.Cu", "width": 0.4,
  "remove_vias": [[135.45, 86.85]], "remove_tracks": [[135.45, 86.85, 133.66, 86.85]],
  "pts": [[133.66, 86.85], [134.2, 86.85], [134.75, 86.3]], "vias": [[134.75, 86.3]], "via_d": 0.8, "via_drill": 0.4},
 {"name": "R12.2 GND -> share D16.3's via (drop via in lane)", "net": "GND", "layer": "B.Cu", "width": 0.4,
  "remove_vias": [[165.5, 111.15]], "remove_tracks": [[166.01, 111.66, 165.5, 111.15]],
  "pts": [[166.01, 112.2], [166.01, 113.0], [d16_gnd_via[0], d16_gnd_via[1]]]},
 {"name": "move GND via near C21 inward", "net": "GND", "layer": "B.Cu", "width": 0.3,
  "remove_vias": [[138.8, 115.55]], "remove_tracks": [[138.8, 114.81, 138.8, 115.55]],
  "pts": [[138.8, 114.81], [139.3, 114.3]], "vias": [[139.3, 114.3]]},
 {"name": "C18.2 GND stub inward", "net": "GND", "layer": "F.Cu", "width": 0.3,
  "remove_vias": [[163.4, 85.9]], "remove_tracks": [[162.8, 86.5, 163.4, 85.9]],
  "pts": [[162.8, 86.5], [162.4, 87.3]], "vias": [[162.4, 87.3]]},
 {"name": "C19.2 GND stub inward", "net": "GND", "layer": "F.Cu", "width": 0.4,
  "remove_vias": [[150.5, 80.25]], "remove_tracks": [[150.48, 81.4, 150.48, 80.27]],
  "pts": [[150.48, 81.4], [150.48, 82.45]], "vias": [[150.48, 82.45]], "via_d": 0.8, "via_drill": 0.4},
 {"name": "C22.2 GND stub inward", "net": "GND", "layer": "F.Cu", "width": 0.4,
  "remove_vias": [[149.5, 119.6]], "remove_tracks": [[149.52, 118.6, 149.52, 119.32]],
  "pts": [[149.52, 118.6], [149.52, 117.3], [148.7, 116.5]], "vias": [[148.7, 116.5]]},   # dock pads CP1/CP3 on B.Cu below; via above them
 {"name": "C21.2 GND stub inward", "net": "GND", "layer": "F.Cu", "width": 0.3,
  "remove_vias": [[136.7, 114.06]], "remove_tracks": [[137.2, 113.5, 136.7, 114.06]],
  "pts": [[137.2, 113.5], [138.2, 113.0]], "vias": [[138.2, 113.0]]},   # FID5 keepout to the west
 {"name": "R24.1 3V3 -> PZ1.1 by trace (drop via in lane)", "net": "3V3", "layer": "B.Cu", "width": 0.3,
  "remove_vias": [[139.9, 83.65]], "remove_tracks": [[139.9, 83.31, 139.9, 83.65], [139.29, 82.7, 139.9, 83.31]],
  "pts": [[139.29, 82.7], [139.29, 83.6], [138.1, 84.8], [138.1, 85.2]]},
 {"name": "TP16 3V3 via inward", "net": "3V3", "layer": "B.Cu", "width": 0.3,
  "remove_vias": [[161.5, 84.75]], "remove_tracks": [[160.45, 83.7, 161.5, 84.75]],
  "pts": [[160.2, 83.7], [160.3, 85.35]], "vias": [[160.3, 85.35]]},
 {"name": "5V via to R11.2 moved inward off the lane", "net": "5V", "layer": "B.Cu", "width": 0.5,
  "remove_vias": [[166.4, 110.3]], "remove_tracks": [[166.4, 110.3, 166.4, 107.65], [162.9, 110.3, 166.4, 110.3]],
  "pts": [[164.2, 110.3], [164.2, 109.4], [165.6, 108.0], [166.45, 107.6]], "vias": [[164.2, 110.3]], "via_d": 0.8, "via_drill": 0.4},
 {"name": "5V F.Cu run shortened to the moved via", "net": "5V", "layer": "F.Cu", "width": 0.5,
  "pts": [[162.9, 110.3], [164.2, 110.3]]},
]
# ---- the ring
A_N0, A_N1 = ang(*pads['D10.2'][:2]), -33.0      # north arc: D10 stub .. transition
A_E0, A_E1 = -29.0, 29.0                         # east crossing at r 22
A_S0, A_S1 = 33.0, ang(*pads['D21.2'][:2])       # south arc: transition .. D21 stub
ring = {"net": "/5V_RING", "layer": "F.Cu", "width": W}
spec += [
 {**ring, "name": "ring north arc", "arcs": [arc(R_RING, A_N0, -90.0), arc(R_RING, -90.0, A_N1)]},
 {**ring, "name": "ring NE link out", "pts": [pt(R_RING, A_N1), pt(R_EAST, A_E0)]},
 {**ring, "name": "ring east arc", "arcs": [arc(R_EAST, A_E0, A_E1)]},
 {**ring, "name": "ring SE link in", "pts": [pt(R_EAST, A_E1), pt(R_RING, A_S0)]},
 {**ring, "name": "ring south arc", "arcs": [arc(R_RING, A_S0, 90.0), arc(R_RING, 90.0, A_S1)]},
]
for ref in ('D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20', 'D21'):
    x, y, n = pads[f'{ref}.2']; a = ang(x, y)
    spec.append({**ring, "name": f"stub {ref}.2", "width": 0.3, "pts": [pt(R_RING, a), [round(x, 3), round(y, 3)]]})
for ref in ('C18', 'C19', 'C20', 'C21', 'C22', 'C23'):
    x, y, n = pads[f'{ref}.1']; a = ang(x, y)
    spec.append({**ring, "name": f"stub {ref}.1", "width": 0.4, "pts": [pt(R_RING, a), [round(x, 3), round(y, 3)]]})
feed_via = pt(21.6, -15.0)
spec += [
 {**ring, "name": "feed via + link to east arc", "width": 0.5, "pts": [feed_via, pt(R_EAST, -15.0)], "vias": [feed_via]},
 {"net": "/5V_RING", "layer": "B.Cu", "width": 0.5, "name": "feed D9.1 -> via (B.Cu)",
  "pts": [list(map(lambda v: round(v, 3), pads['D9.1'][:2])), [159.85, 96.9], [168.3, 96.9], feed_via]},
]
out = Path(__file__).with_name('5v-ring.json'); out.write_text(json.dumps(spec, indent=1)); print('wrote', out, len(spec), 'entries; D16 GND via', d16_gnd_via)
