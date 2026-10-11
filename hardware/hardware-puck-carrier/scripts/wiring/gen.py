"""Generate the wired schematic from plan.py.

Pipeline: preprocess text (remove USB-C parts, patch CP values, fix SHLD pin
types, embed U11 + XL-1010RGBC lib symbols) -> parse -> emit stubs/labels/NCs/
new symbols.

Reproduce the wired schematic from the repo (KiCad closed):
    cd scripts/wiring
    python3 gen.py ../../puck-carrier.kicad_sch.pre-wiring out.kicad_sch
    kicad-cli sch export netlist out.kicad_sch -o out.net
    python3 verify.py out.net        # needs inv.json + expected_nets.json (gen.py writes the latter)
Last run 2026-08-31 (hole-removal pass, after Block 10b glow-ring pass): netlist diff EMPTY,
ERC 0 errors / 2 accepted warnings on the installed project.
"""
import sys, math, uuid, json, re
from sexp import parse, find, find_all, atom
from plan import (PLAN, UJOINS, PAIRJOINS, REMOVE_REFS, NEW_SYMBOLS,
                  PATCH_VALUES)

SRC = sys.argv[1]
DST = sys.argv[2]

with open(SRC) as f:
    text = f.read()

# ---------- text preprocessing ----------
def symbol_blocks(t):
    """Yield (start, end, block) for every depth-1 instance symbol block."""
    for m in re.finditer(r'\t\(symbol\n', t):
        start = m.start()
        depth = 0
        i = start
        while True:
            c = t[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield start, i + 1, t[start:i + 1]

# 1. remove J2 / R18 / R19
removed = []
for ref in REMOVE_REFS:
    for s, e, blk in symbol_blocks(text):
        if '(property "Reference" "%s"' % ref in blk:
            end = e
            if text[end] == '\n':
                end += 1
            text = text[:s] + text[end:]
            removed.append(ref)
            break
assert sorted(removed) == sorted(REMOVE_REFS), removed

# 2. patch CP1/CP2 Value + Footprint inside their blocks only
for ref, (newval, newfp) in PATCH_VALUES.items():
    for s, e, blk in symbol_blocks(text):
        if '(property "Reference" "%s"' % ref in blk:
            nb = re.sub(r'\(property "Value" "[^"]*"',
                        '(property "Value" "%s"' % newval, blk, count=1)
            nb = re.sub(r'\(property "Footprint" "[^"]*"',
                        '(property "Footprint" "%s"' % newfp, nb, count=1)
            assert nb != blk
            text = text[:s] + nb + text[e:]
            break
    else:
        raise AssertionError(ref)

# 3. FDC1004 SHLD1/SHLD2: input -> output (guard driver pins) in embedded def
i = text.index('(symbol "puck-extra:FDC1004DGSR"')
depth = 0
j = i
while True:
    c = text[j]
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth == 0:
            break
    j += 1
fdc = text[i:j + 1]
nfdc = fdc
for coord in ('-17.78 -2.54', '-17.78 -5.08'):   # SHLD1 pin 1, SHLD2 pin 6
    pat = '(pin input line\n\t\t\t\t\t(at %s 0)' % coord
    rep = '(pin output line\n\t\t\t\t\t(at %s 0)' % coord
    assert pat in nfdc, coord
    nfdc = nfdc.replace(pat, rep)
text = text[:i] + nfdc + text[j + 1:]

# 4. embed new lib symbols (U11 USBLC6, XL-1010RGBC ring LED)
k = text.index('\t(lib_symbols\n') + len('\t(lib_symbols\n')
embed = (open('usblc6_embed.sexp').read() +
         open('xl1010_embed.sexp').read())
text = text[:k] + embed + text[k:]

# ---------- parse ----------
doc = parse(text)
root = doc[0]

libs = find(root, 'lib_symbols')
libpins = {}
for ls in find_all(libs, 'symbol'):
    lid = atom(ls[1])
    pins = []
    for sub in find_all(ls, 'symbol'):
        for p in find_all(sub, 'pin'):
            at = find(p, 'at'); name = find(p, 'name'); num = find(p, 'number')
            hide = find(p, 'hide')
            pins.append({'etype': str(p[1]),
                         'x': float(atom(at[1])), 'y': float(atom(at[2])),
                         'angle': float(atom(at[3])) if len(at) > 3 else 0.0,
                         'name': atom(name[1]), 'num': atom(num[1]),
                         'hide': bool(hide and atom(hide[1]) == 'yes')})
    libpins[lid] = pins

insts = {}
for s in find_all(root, 'symbol'):
    lid = atom(find(s, 'lib_id')[1])
    at = find(s, 'at')
    x, y = float(atom(at[1])), float(atom(at[2]))
    rot = float(atom(at[3])) if len(at) > 3 else 0.0
    mir = find(s, 'mirror')
    ref = None
    for prop in find_all(s, 'property'):
        if atom(prop[1]) == 'Reference':
            ref = atom(prop[2])
    insts[ref] = {'lib_id': lid, 'x': x, 'y': y, 'rot': rot,
                  'mirror': atom(mir[1]) if mir else None}

for ref, tup in NEW_SYMBOLS.items():
    lid, x, y, val, fp = tup[:5]
    rot = float(tup[5]) if len(tup) > 5 else 0.0
    assert ref not in insts, ref
    insts[ref] = {'lib_id': lid, 'x': x, 'y': y, 'rot': rot, 'mirror': None}

def pin_info(ref, num):
    inst = insts[ref]
    for p in libpins[inst['lib_id']]:
        if p['num'] == str(num):
            m, rot = inst['mirror'], inst['rot']
            px, py, ang = p['x'], p['y'], p['angle']
            def xf(lx, ly):
                if m == 'x': ly = -ly
                elif m == 'y': lx = -lx
                r = math.radians(rot)
                return (inst['x'] + lx*math.cos(r) - ly*math.sin(r),
                        inst['y'] - (lx*math.sin(r) + ly*math.cos(r)))
            ax, ay = xf(px, py)
            a = math.radians(ang + 180.0)
            dx0, dy0 = math.cos(a), math.sin(a)
            if m == 'x': dy0 = -dy0
            elif m == 'y': dx0 = -dx0
            r = math.radians(rot)
            dx = dx0*math.cos(r) - dy0*math.sin(r)
            dy = -(dx0*math.sin(r) + dy0*math.cos(r))
            return (round(ax, 2), round(ay, 2), round(dx), round(dy), p)
    raise KeyError((ref, num))

def uid():
    return str(uuid.uuid4())

def fnum(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return s if s else '0'

OUT = []
def emit_wire(x1, y1, x2, y2):
    OUT.append('\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n'
               '\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n'
               '\t\t(uuid "%s")\n\t)' % (fnum(x1), fnum(y1), fnum(x2), fnum(y2), uid()))

def emit_nc(x, y):
    OUT.append('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)'
               % (fnum(x), fnum(y), uid()))

def emit_label(net, x, y, ang, kind):
    just = 'left' if ang in (0, 90) else 'right'
    if kind == 'G':
        OUT.append('\t(global_label "%s"\n\t\t(shape passive)\n\t\t(at %s %s %d)\n'
                   '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
                   '\t\t\t(justify %s)\n\t\t)\n\t\t(uuid "%s")\n\t)'
                   % (net, fnum(x), fnum(y), ang, just, uid()))
    else:
        OUT.append('\t(label "%s"\n\t\t(at %s %s %d)\n'
                   '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
                   '\t\t\t(justify %s bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)'
                   % (net, fnum(x), fnum(y), ang, just, uid()))

def dir_angle(dx, dy):
    if dx > 0: return 0
    if dx < 0: return 180
    if dy < 0: return 90
    return 270

covered = set()
expected = {}
def expect(net, ref, pin):
    expected.setdefault(net, set()).add((ref, str(pin)))

wire_count = label_count = nc_count = 0
done_wires = set()
for (ref, pin), action in sorted(PLAN.items()):
    x, y, dx, dy, p = pin_info(ref, pin)
    kind = action[0]
    covered.add((ref, str(pin)))
    if kind == 'NC':
        emit_nc(x, y); nc_count += 1
        continue
    if kind in ('G', 'L'):
        net = action[1]
        opts = action[2] if len(action) > 2 else {}
        L = opts.get('len', 2.54)
        ex, ey = x + dx*L, y + dy*L
        emit_wire(x, y, ex, ey); wire_count += 1
        ang = opts.get('ang')
        if ang is None:
            ang = dir_angle(dx, dy)
        emit_label(net, ex, ey, ang, kind); label_count += 1
        expect(net, ref, pin)
        continue
    if kind == 'PIN_L':
        net, ang = action[1], action[2]
        emit_label(net, x, y, ang, 'L'); label_count += 1
        expect(net, ref, pin)
        continue
    if kind == 'W':
        ref2, pin2, netid = action[1], action[2], action[3]
        key = tuple(sorted([(ref, str(pin)), (ref2, str(pin2))]))
        expect(netid, ref, pin)
        if key in done_wires:
            continue
        done_wires.add(key)
        x2, y2, _, _, _ = pin_info(ref2, pin2)
        assert x == x2 or y == y2, ('W not axis-aligned', ref, pin, ref2, pin2)
        emit_wire(x, y, x2, y2); wire_count += 1
        continue
    if kind == 'WL':
        ref2, pin2, net, lkind, (lx, ly), ang = action[1:]
        x2, y2, _, _, _ = pin_info(ref2, pin2)
        assert x == x2 or y == y2, ('WL not axis-aligned', ref, pin, ref2, pin2)
        emit_wire(x, y, x2, y2); wire_count += 1
        assert (min(x,x2) <= lx <= max(x,x2) and min(y,y2) <= ly <= max(y,y2)), \
            ('WL label off wire', ref, pin)
        emit_label(net, lx, ly, ang, lkind); label_count += 1
        expect(net, ref, pin)
        expect(net, ref2, pin2)
        covered.add((ref2, str(pin2)))
        continue
    raise ValueError(action)

for (ra, pa), (rb, pb), drop, net, lkind, ang in UJOINS:
    xa, ya, dxa, dya, _ = pin_info(ra, pa)
    xb, yb, dxb, dyb, _ = pin_info(rb, pb)
    assert (dxa, dya) == (dxb, dyb)
    exa, eya = xa + dxa*drop, ya + dya*drop
    exb, eyb = xb + dxb*drop, yb + dyb*drop
    emit_wire(xa, ya, exa, eya); emit_wire(xb, yb, exb, eyb)
    emit_wire(exa, eya, exb, eyb); wire_count += 3
    emit_label(net, exa, eya, ang, lkind); label_count += 1
    expect(net, ra, pa); expect(net, rb, pb)
    covered.add((ra, str(pa))); covered.add((rb, str(pb)))

missing = []
for ref, inst in insts.items():
    for p in libpins[inst['lib_id']]:
        if p['hide']:
            continue
        if (ref, p['num']) not in covered:
            missing.append((ref, p['num'], p['name']))
if missing:
    print('MISSING PINS:', missing)
    sys.exit(1)

# ---------- new symbol instances ----------
PROP_OFFSETS = {   # lib_id -> (ref dx,dy, value dx,dy)
    'Device:R': (0, -5.84, 0, 5.84),
    'Connector:TestPoint': (0, -6.09, 0, 2.03),
    'Connector_Generic:Conn_01x01': (-1.9, -3.3, -1.9, 3.3),
    'puck-extra:USBLC6-2SC6': (8.89, -10.16, 8.89, 10.16),
    'Device:C': (2.54, -1.27, 2.54, 1.27),
    'Device:LED': (6.35, -2.54, 6.35, 2.54),
    'Diode:SS34': (0, -3.81, 0, 3.81),
    'power:PWR_FLAG': (0, -4.57, 0, 2.03),
    'puck-extra:XL-1010RGBC': (-6.35, -8.89, 0, 6.35),
}

def prop(name, val, px, py, hide=False):
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %s %s 0)\n%s'
            '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n'
            '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n'
            '\t\t\t\t)\n\t\t\t)\n\t\t)\n'
            % (name, val, fnum(px), fnum(py),
               '\t\t\t(hide yes)\n' if hide else ''))

def make_symbol(ref, lid, x, y, val, fp, rot=0):
    rdx, rdy, vdx, vdy = PROP_OFFSETS[lid]
    pins = sorted({p['num'] for p in libpins[lid]}, key=lambda n: (len(n), n))
    s = '\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %s %s %d)\n\t\t(unit 1)\n' % (lid, fnum(x), fnum(y), rot)
    s += ('\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n'
          '\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n'
          '\t\t(fields_autoplaced yes)\n\t\t(uuid "%s")\n' % uid())
    s += prop('Reference', ref, x + rdx, y + rdy, hide=ref.startswith('#'))
    s += prop('Value', val, x + vdx, y + vdy)
    s += prop('Footprint', fp, x, y, hide=True)
    s += prop('Datasheet', '', x, y, hide=True)
    s += prop('Description', 'added 2026-08-31 dock/USB delta', x, y, hide=True)
    for n in pins:
        s += '\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)\n' % (n, uid())
    s += ('\t\t(instances\n\t\t\t(project "puck-carrier"\n'
          '\t\t\t\t(path "/331902f6-e258-4dcd-9927-c36789212c93"\n'
          '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n'
          '\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)' % ref)
    return s

newsyms = [make_symbol(ref, *NEW_SYMBOLS[ref]) for ref in sorted(NEW_SYMBOLS)]

insertion = '\n'.join(OUT) + '\n' + '\n'.join(newsyms) + '\n'
marker = '\t(sheet_instances'
idx = text.rindex(marker)
newtext = text[:idx] + insertion + text[idx:]
with open(DST, 'w') as f:
    f.write(newtext)

with open('expected_nets.json', 'w') as f:
    json.dump({k: sorted(list(v)) for k, v in expected.items()}, f, indent=1)

print('wires=%d labels=%d no_connects=%d nets=%d symbols=%d' %
      (wire_count, label_count, nc_count, len(expected), len(insts)))
print('wrote', DST)
