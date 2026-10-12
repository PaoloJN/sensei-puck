"""Move module nets to spare MDBT50Q pads (schematic + board, textual edits).

python3 pin_swap.py sch_in sch_out pcb_in pcb_out
MOVES: net, old pad, old pin point, old label point, new pad, new pin point (left side of the symbol).
"""
import re, sys, uuid
from pathlib import Path
MOVES = [  # net, old pad, (old pin), (old label), new pad, (new pin), (new label), new pinfunction
    ('EC_SENSE_A', '20', (43.18, 55.88), (40.64, 55.88), '12', (43.18, 68.58), (40.64, 68.58)),
    ('PDM_DATA',   '22', (83.82, 55.88), (86.36, 55.88), '4',  (43.18, 114.3), (40.64, 114.3)),
    ('PDM_CLK',    '24', (83.82, 58.42), (86.36, 58.42), '6',  (43.18, 119.38), (40.64, 119.38)),
    ('BTN_FRESET', '26', (83.82, 116.84), (86.36, 116.84), '8', (43.18, 124.46), (40.64, 124.46)),
]
def f(v): return ('%g' % v)
sch_in, sch_out, pcb_in, pcb_out = sys.argv[1:5]
s = Path(sch_in).read_text()
for net, opad, (ox, oy), (fx, fy), npad, (nx, ny), (nfx, nfy) in MOVES:
    # 1. drop the no_connect on the new pin
    s, n = re.subn(r'\t\(no_connect\n\t\t\(at %s %s\)\n\t\t\(uuid "[^"]+"\)\n\t\)\n' % (f(nx), f(ny)), '', s); assert n == 1, ('no_connect', net, n)
    # 2. move the stub wire
    s, n = re.subn(r'\(wire\n\t\t\(pts\n\t\t\t\(xy %s %s\)\n\t\t\t\(xy %s %s\)' % (f(ox), f(oy), f(fx), f(fy)),
                   '(wire\n\t\t(pts\n\t\t\t(xy %s %s)\n\t\t\t(xy %s %s)' % (f(nx), f(ny), f(nfx), f(nfy)), s); assert n == 1, ('wire', net, n)
    # 3. move the global label and flip it to the left-side style
    pat = r'(\(global_label "%s"\n\t\t\(shape passive\)\n\t\t\(at )%s %s \d+(\)\n\t\t\(effects\n\t\t\t\(font\n\t\t\t\t\(size 1.27 1.27\)\n\t\t\t\)\n\t\t\t\(justify )\w+' % (re.escape(net), f(fx), f(fy))
    s, n = re.subn(pat, r'\g<1>%s %s 180\g<2>right' % (f(nfx), f(nfy)), s); assert n == 1, ('label', net, n)
    s, n = re.subn(r'(\(property "Intersheetrefs" "\$\{INTERSHEET_REFS\}"\n\t\t\t\(at )%s %s 0\)' % (f(fx), f(fy)), r'\g<1>%s %s 0)' % (f(nfx), f(nfy)), s); assert n == 1, ('isr', net, n)
    # 4. no_connect on the old pin
    s = s.replace('\t(sheet_instances', '\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)\n\t(sheet_instances' % (f(ox), f(oy), uuid.uuid4()), 1)
Path(sch_out).write_text(s); print('schematic:', len(MOVES), 'labels moved')
b = Path(pcb_in).read_text()
i = b.find('(property "Reference" "U1"'); start = b.rfind('(footprint', 0, i); end = b.find('\n\t(footprint', i); end = len(b) if end < 0 else end
fp = b[start:end]
for net, opad, *_ , npad, _, _ in [(m[0], m[1], m[4], m[5], m[6]) for m in MOVES]:
    pass
for m in MOVES:
    net, opad, npad = m[0], m[1], m[4]
    mo = re.search(r'\(pad "%s" smd.*?\n\t\t\)' % opad, fp, re.S); block = mo.group(0)
    netm = re.search(r"\n\t\t\t\(net (?:\d+ )?\"%s\"\)" % re.escape(net), block); assert netm, (net, opad)
    newold = block.replace(netm.group(0), '', 1)
    fp = fp.replace(block, newold, 1)
    mn = re.search(r'\(pad "%s" smd.*?\n\t\t\)' % npad, fp, re.S); nb = mn.group(0); assert '(net ' not in nb, (npad, 'already has a net')
    nb2 = re.sub(r'(\n\t\t\t\(pinfunction )', netm.group(0) + r'\1', nb, count=1); assert nb2 != nb
    fp = fp.replace(nb, nb2, 1)
Path(pcb_out).write_text(b[:start] + fp + b[end:]); print('board: pad nets moved')
