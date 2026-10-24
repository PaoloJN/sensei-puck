"""East column of U1 (pads 16-26), 2026-10-16 evening plan.

North trio (SCL 16, SDA 17; BTN_DFU 18 reserved at x 145.05): B.Cu columns up the C3
corridor, via at the corridor top (outside the FDC via disc), PWR rows east to the
U4.9 / U4.10 vias placed by i2c-north.json.
South four (EXP_00 20, EXP_01 22, LED_STAT 24, CHG_STAT 26): 0.1 mm B.Cu columns
(higher pad = outer column), 0.1 mm lane rows under U8 at 0.3 pitch, vias in a
staircase just outside the FDC disc (x > 148.4 + sqrt(6.45^2 - dy^2) + 0.25), then PWR
to the destinations: EXP_00/EXP_01 back up to B.Cu at x ~158 and east to TP25/TP26,
LED_STAT down to R31.1, CHG_STAT down to U7.1.
"""
import json, pathlib
V = 0.5; VD = 0.2
E = []
def e(name, net, layer, w, pts, vias=(), **kw):
    d = {"name": name, "net": net, "layer": layer, "width": w, "pts": pts}
    if vias: d["vias"] = list(vias); d["via_d"] = V; d["via_drill"] = VD
    d.update(kw); E.append(d)

# --- north: SCL pad 16, SDA pad 17
e("SCL: pad 16 up the corridor to a via at the top", "SCL", "B.Cu", 0.15,
  [[143.45, 96.0], [144.2, 96.0], [144.2, 94.0]], [[144.2, 94.0]])
e("SCL: PWR row y 94.35 east to the U4.9 via", "SCL", "In2.Cu", 0.2,
  [[144.2, 94.0], [144.55, 94.35], [151.9, 94.35], [152.0, 94.35]])
e("SDA: pad 17 up the corridor (outer column) to a via", "SDA", "B.Cu", 0.15,
  [[143.45, 96.8], [144.75, 96.8], [144.75, 93.4]], [[144.75, 93.4]])
e("SDA: PWR row y 92.95 east, up into the U4.10 via", "SDA", "In2.Cu", 0.2,
  [[144.75, 93.4], [145.2, 92.95], [151.05, 92.95], [151.5, 93.4], [151.5, 93.8]])

# --- south four: columns, lane rows, staircase vias
cols = {"EXP_00": (20, 98.4, 145.35, 102.95), "EXP_01": (22, 99.2, 145.05, 103.25),
        "LED_STAT": (24, 100.0, 144.75, 103.55), "CHG_STAT": (26, 100.8, 144.45, 103.85)}
ends = {"EXP_00":  [[154.3, 102.95], [154.5, 103.15], [154.75, 103.15]],
        "EXP_01":  [[153.6, 103.25], [153.9, 103.55], [154.15, 103.55]],
        "LED_STAT": [[153.15, 103.55], [153.75, 104.15]],
        "CHG_STAT": [[152.45, 103.85], [153.3, 104.7]]}
for net, (pad, py, cx, ry) in cols.items():
    pts = [[143.45, py], [cx, py], [cx, ry - 0.3], [cx + 0.3, ry]] + ends[net]
    e(f"{net}: pad {pad} east, down column x {cx}, lane row y {ry}, via", net, "B.Cu", 0.1,
      pts, [ends[net][-1]])

# --- PWR legs and far ends
e("EXP_00: PWR row y 103.2 east, drop to a via at (158.4,104.2)", "EXP_00", "In2.Cu", 0.15,
  [[154.75, 103.15], [154.8, 103.2], [158.15, 103.2], [158.4, 103.45], [158.4, 104.2]], [[158.4, 104.2]])
e("EXP_00: B.Cu y 104.6 east under R3/TP6, down x 167.4 into TP25", "EXP_00", "B.Cu", 0.1,
  [[158.4, 104.2], [158.8, 104.6], [167.05, 104.6], [167.4, 104.95], [167.4, 106.95], [167.75, 107.3], [168.8, 107.3]])
e("EXP_01: PWR row y 103.65 east, drop to a via at (157.7,104.5)", "EXP_01", "In2.Cu", 0.15,
  [[154.15, 103.55], [154.25, 103.65], [157.45, 103.65], [157.7, 103.9], [157.7, 104.5]], [[157.7, 104.5]])
e("EXP_01: B.Cu y 105.0 east, down x 167.1 into TP26", "EXP_01", "B.Cu", 0.1,
  [[157.7, 104.5], [158.2, 105.0], [166.75, 105.0], [167.1, 105.35], [167.1, 109.25], [167.45, 109.6], [168.6, 109.6]])
e("LED_STAT: PWR east to x 156.65, south to y 112.5, east to a via by R31.1", "LED_STAT", "In2.Cu", 0.15,
  [[153.75, 104.15], [156.3, 104.15], [156.65, 104.5], [156.65, 112.25], [156.9, 112.5], [159.3, 112.5]], [[159.3, 112.5]])
e("LED_STAT: B.Cu stub into R31.1", "LED_STAT", "B.Cu", 0.15, [[159.3, 112.5], [158.51, 112.5]])
e("CHG_STAT: PWR south along x 152.7 to a via under U7.1", "CHG_STAT", "In2.Cu", 0.15,
  [[153.3, 104.7], [152.7, 105.3], [152.7, 109.75], [153.0, 110.05]], [[153.0, 110.05]])
e("CHG_STAT: B.Cu stub into U7.1", "CHG_STAT", "B.Cu", 0.15, [[153.0, 110.05], [153.0, 109.65], [153.1625, 109.65]])

out = pathlib.Path(__file__).with_name("east-column.json")
out.write_text(json.dumps(E, indent=1)); print(len(E), "entries ->", out)
