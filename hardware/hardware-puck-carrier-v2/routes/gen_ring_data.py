"""RING_D1..D11 (not D6): LED DOUT (pad 1, r 20.1) -> next LED DIN (pad 4, r 20.9) as rounded arcs on F.Cu.
Arc at r 20.1 past pad 1, short link outward, arc at r 20.9 into pad 4. 0.25 mm (ring class)."""
import math, json, pcbnew, sys
from pathlib import Path
b = pcbnew.LoadBoard(sys.argv[1]); tomm = pcbnew.ToMM
CX, CY = 150.0, 100.0
def pt(r, a): return [round(CX + r * math.cos(math.radians(a)), 3), round(CY + r * math.sin(math.radians(a)), 3)]
def arc(r, a0, a1): return [*pt(r, a0), *pt(r, (a0 + a1) / 2), *pt(r, a1)]
pads = {}
for f in b.GetFootprints():
    for p in f.Pads(): pads[f'{f.GetReference()}.{p.GetNumber()}'] = (tomm(p.GetPosition().x), tomm(p.GetPosition().y), p.GetNetname())
def ang(x, y): return math.degrees(math.atan2(y - CY, x - CX))
order = ['D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20', 'D21']
spec = []
for a, b_ in zip(order, order[1:]):
    x1, y1, net = pads[f'{a}.1']; x4, y4, net4 = pads[f'{b_}.4']
    assert net == net4, (a, b_, net, net4)
    if net == '/RING_D6': continue          # east crossing past the EC fingers: separate plan
    a1, a4 = ang(x1, y1), ang(x4, y4)
    r1, r4 = math.hypot(x1 - CX, y1 - CY), math.hypot(x4 - CX, y4 - CY)
    e = {"name": f"{net} {a}.1 -> {b_}.4", "net": net, "layer": "F.Cu", "width": 0.25,
         "arcs": [arc(r1, a1, a4 - 3.6), arc(r4, a4 - 2.2, a4)],
         "pts": [pt(r1, a4 - 3.6), pt(r4, a4 - 2.2)]}
    spec.append(e)
out = Path(__file__).with_name('ring-data.json'); out.write_text(json.dumps(spec, indent=1)); print('wrote', out, len(spec))
