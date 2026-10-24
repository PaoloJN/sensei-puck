"""Move module nets to spare MDBT50Q pads (schematic + board, textual edits, KiCad 10 format).

python3 pin_swap_v2.py sch_in sch_out pcb_in pcb_out
Each move: the stub wire between the U1 pin and its global label is re-pointed at the new pin,
the label moves beside the new pin (left-side style), the no_connect on the new pin is removed
and one is added on the old pin; on the board the pad net moves from the old pad to the new.
"""
import re, sys, uuid
from pathlib import Path
MOVES_1 = [  # 2026-10-16 pass 1 (applied): net, old pad, old pin xy, old label xy, new pad, new pin xy, new label xy
    ('EC_SENSE_A', '20', (43.18, 55.88), (40.64, 55.88), '12', (43.18, 68.58), (40.64, 68.58)),
    ('PDM_DATA',   '22', (83.82, 55.88), (86.36, 55.88), '4',  (43.18, 114.3), (40.64, 114.3)),
    ('PDM_CLK',    '24', (83.82, 58.42), (86.36, 58.42), '6',  (43.18, 119.38), (40.64, 119.38)),
    ('BTN_FRESET', '26', (83.82, 116.84), (86.36, 116.84), '8', (43.18, 124.46), (40.64, 124.46)),
]
MOVES_2 = [  # 2026-10-16 pass 2: pin assignment follows the escape plan (east column -> south lane, spare pads that exit directly)
    ('CHG_STAT', '23', (83.82, 119.38), (86.36, 119.38), '20', (43.18, 55.88), (40.64, 55.88)),
    ('BTN_DFU',  '25', (43.18, 109.22), (40.64, 109.22), '22', (83.82, 55.88), (86.36, 55.88)),
    ('LED_STAT', '29', (83.82, 111.76), (86.36, 111.76), '24', (83.82, 58.42), (86.36, 58.42)),
    ('SDA',      '19', (83.82, 101.6),  (86.36, 101.6),  '26', (83.82, 116.84), (86.36, 116.84)),
    ('LED_850',  '36', (83.82, 66.04),  (86.36, 66.04),  '50', (43.18, 93.98), (40.64, 93.98)),
    ('OW_DQ',    '38', (83.82, 71.12),  (86.36, 71.12),  '3',  (43.18, 111.76), (40.64, 111.76)),
]
import os
MOVES = MOVES_2 if os.environ.get('SWAP_PASS', '2') == '2' else MOVES_1
U1_X = 63.5   # symbol centre: pins left of it get a left-side label (rot 180, justify right)
def f(v): return '%g' % v
sch_in, sch_out, pcb_in, pcb_out = sys.argv[1:5]
s = Path(sch_in).read_text()
for net, opad, (ox, oy), (fx, fy), npad, (nx, ny), (nfx, nfy) in MOVES:
    s, n = re.subn(r'\t\(no_connect\n\t\t\(at %s %s\)\n\t\t\(uuid "[^"]+"\)\n\t\)\n' % (f(nx), f(ny)), '', s); assert n == 1, ('no_connect', net, n)
    pat = r'\(wire\n\t\t\(pts\n\t\t\t\(xy %s %s\) \(xy %s %s\)' 
    s, n = re.subn(pat % (f(ox), f(oy), f(fx), f(fy)), '(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)' % (f(nx), f(ny), f(nfx), f(nfy)), s)
    if n == 0: s, n = re.subn(pat % (f(fx), f(fy), f(ox), f(oy)), '(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)' % (f(nfx), f(nfy), f(nx), f(ny)), s)
    assert n == 1, ('wire', net, n)
    pat = r'(\(global_label "%s"\n\t\t\(shape \w+\)\n\t\t\(at )%s %s \d+(\)\n\t\t\(effects\n\t\t\t\(font\n\t\t\t\t\(size 1.27 1.27\)\n\t\t\t\)\n\t\t\t\(justify )\w+' % (re.escape(net), f(fx), f(fy))
    rot, just = (180, 'right') if nx < U1_X else (0, 'left')
    s, n = re.subn(pat, r'\g<1>%s %s %d\g<2>%s' % (f(nfx), f(nfy), rot, just), s); assert n == 1, ('label', net, n)
    s, n = re.subn(r'(\(property "Intersheetrefs" "\$\{INTERSHEET_REFS\}"\n\t\t\t\(at )%s %s 0\)' % (f(fx), f(fy)), r'\g<1>%s %s 0)' % (f(nfx), f(nfy)), s); assert n == 1, ('isr', net, n)
    s = s.replace('\t(sheet_instances', '\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)\n\t(sheet_instances' % (f(ox), f(oy), uuid.uuid4()), 1)
Path(sch_out).write_text(s); print('schematic:', len(MOVES), 'labels moved')
b = Path(pcb_in).read_text()
i = b.find('(property "Reference" "U1"'); start = b.rfind('(footprint', 0, i); end = b.find('\n\t(footprint', i); end = len(b) if end < 0 else end
fp = b[start:end]
for m in MOVES:
    net, opad, npad = m[0], m[1], m[4]
    mo = re.search(r'\(pad "%s" smd.*?\n\t\t\)' % opad, fp, re.S); block = mo.group(0)
    netm = re.search(r'\n\t\t\t\(net (?:\d+ )?"%s"\)' % re.escape(net), block); assert netm, (net, opad)
    fp = fp.replace(block, block.replace(netm.group(0), '', 1), 1)
    mn = re.search(r'\(pad "%s" smd.*?\n\t\t\)' % npad, fp, re.S); nb = mn.group(0); assert '(net ' not in nb, (npad, 'already has a net')
    nb2 = re.sub(r'(\n\t\t\t\(pinfunction )', netm.group(0) + r'\1', nb, count=1); assert nb2 != nb, (npad, 'no pinfunction anchor')
    fp = fp.replace(nb, nb2, 1)
Path(pcb_out).write_text(b[:start] + fp + b[end:]); print('board: pad nets moved')
