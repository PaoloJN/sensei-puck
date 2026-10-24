"""RING_D6: D15.1 -> D16.4 past the EC fingers. F.Cu is full (fingers, 5V ring links, LED GND vias), so the
hop drops to B.Cu and runs as an arc at r 22.25, just inside KO_RIM (r 22.35) and outside the TP column."""
import math, json
from pathlib import Path
CX, CY = 150.0, 100.0
def pt(r, a): return [round(CX + r * math.cos(math.radians(a)), 3), round(CY + r * math.sin(math.radians(a)), 3)]
def arc(r, a0, a1): return [*pt(r, a0), *pt(r, (a0 + a1) / 2), *pt(r, a1)]
D15_1 = [166.21, 88.10]; D16_4 = [166.84, 112.39]
v1 = pt(20.2, -34.3); v2 = pt(21.5, 36.3)
spec = [
 {"name": "RING_D6 D15.1 -> via (F.Cu)", "net": "/RING_D6", "layer": "F.Cu", "width": 0.25, "pts": [D15_1, v1], "vias": [v1], "via_d": 0.5, "via_drill": 0.2},
 {"name": "RING_D6 B.Cu arc at r 22.25 around the east", "net": "/RING_D6", "layer": "B.Cu", "width": 0.15,
  "pts": [v1, pt(22.25, -32.0)], "arcs": [arc(22.25, -32.0, 36.3)], "vias": [v2], "via_d": 0.5, "via_drill": 0.2},
 {"name": "RING_D6 B.Cu arc end -> via", "net": "/RING_D6", "layer": "B.Cu", "width": 0.15, "pts": [pt(22.25, 36.3), v2]},
 {"name": "RING_D6 via -> D16.4 (F.Cu)", "net": "/RING_D6", "layer": "F.Cu", "width": 0.25, "pts": [v2, D16_4]},
]
out = Path(__file__).with_name('ring-d6.json'); out.write_text(json.dumps(spec, indent=1)); print('wrote', out)
