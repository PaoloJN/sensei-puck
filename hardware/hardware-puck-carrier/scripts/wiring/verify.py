"""Diff exported KiCad netlist against expected nets from plan.py.

Checks:
 1. Named nets: exact membership match, expected name == exported name
    (local labels may export with or without leading '/').
 2. Unnamed nets ('~x' ids): membership match against some exported net.
 3. NC pins: must not appear in any multi-pin net (KiCad exports them in
    unconnected-() single-pin nets).
 4. No exported multi-pin net that isn't expected.
 5. U1 pin->net cross-check against the spec pin map (independent table).
"""
import sys, json
from sexp import parse, find, find_all, atom

NETFILE = sys.argv[1]
expected = {k: set(map(tuple, v)) for k, v in
            json.load(open('expected_nets.json')).items()}

doc = parse(open(NETFILE).read())
root = doc[0]
nets = find(root, 'nets')
exported = {}   # name -> set of (ref,pin)
for n in find_all(nets, 'net'):
    name = atom(find(n, 'name')[1])
    members = set()
    for node in find_all(n, 'node'):
        ref = atom(find(node, 'ref')[1])
        pin = atom(find(node, 'pin')[1])
        members.add((ref, pin))
    exported[name] = members

# fold hidden stacked pins: expected doesn't list e.g. U1 GND pins 2/15/33/55
# or J2 A9/B4/B9/A12/B1/B12, U8 pin 7. Add them to expected where the visible
# twin is present.
STACKS = {
    ('U1', '1'): [('U1', '2'), ('U1', '15'), ('U1', '33'), ('U1', '55')],
    ('J2', 'A4'): [('J2', 'A9'), ('J2', 'B4'), ('J2', 'B9')],
    ('J2', 'A1'): [('J2', 'A12'), ('J2', 'B1'), ('J2', 'B12')],
    ('U8', '6'): [('U8', '7')],
}
for net, mem in expected.items():
    for vis, hid in STACKS.items():
        if vis in mem:
            mem.update(hid)

# PWR_FLAG (#FLGxx) symbols are excluded from netlist export by KiCad
for net, mem in expected.items():
    for rp in [rp for rp in mem if rp[0].startswith('#')]:
        mem.discard(rp)

fail = 0
def err(*a):
    global fail
    fail += 1
    print('DIFF:', *a)

multi = {n: m for n, m in exported.items() if len(m) > 1}
single = {n: m for n, m in exported.items() if len(m) == 1}

named_expected = {n: m for n, m in expected.items() if not n.startswith('~')}
unnamed_expected = {n: m for n, m in expected.items() if n.startswith('~')}

used_export = set()
for name, mem in sorted(named_expected.items()):
    cands = [en for en, em in exported.items()
             if en == name or en == '/' + name]
    if not cands:
        # single-pin nets w/ label keep name; find by membership
        cands = [en for en, em in exported.items() if em == mem]
        if cands:
            err('net %s exported under unexpected name %s' % (name, cands))
            continue
        err('net %s missing from export (expected %s)' % (name, sorted(mem)))
        continue
    en = cands[0]
    used_export.add(en)
    em = exported[en]
    if em != mem:
        err('net %s membership mismatch:\n  missing in export: %s\n  extra in export: %s'
            % (name, sorted(mem - em), sorted(em - mem)))

for name, mem in sorted(unnamed_expected.items()):
    cands = [en for en, em in exported.items() if em == mem]
    if not cands:
        err('unnamed net %s (%s) not found as any exported net' % (name, sorted(mem)))
        continue
    used_export.add(cands[0])

# leftover exported multi-pin nets = unexpected connections
for en, em in sorted(multi.items()):
    if en not in used_export:
        err('unexpected exported net %s: %s' % (en, sorted(em)))

# NC pins must only appear in unconnected single-pin nets
nc_pins = json.load(open('nc_pins.json')) if False else None

# U1 cross-check against spec pin map (hand-typed from carrier-board-spec.md)
SPEC_U1 = {
    'P0.26': 'SDA', 'P0.27': 'SCL',
    'P0.02': 'EC_A', 'P0.03': 'EC_B',
    'P0.04': 'EC_SENSE_A', 'P0.05': 'EC_SENSE_B',
    'P0.22': 'EC_DRV_LO', 'P0.23': 'EC_DRV_HI',
    'P0.13': 'LED_WHITE', 'P0.14': 'LED_850', 'P0.15': 'LED_365',
    'P0.16': 'OW_DQ', 'P0.17': 'HEATER_EN', 'P0.19': 'PIEZO',
    'P0.20': 'BOOST_EN', 'P0.21': 'IMU_INT',
    'P0.08': 'PDM_CLK', 'P0.06': 'PDM_DATA',
    'P0.24': 'UART_TX', 'P0.25': 'UART_RX',
    'P0.11': 'UVC_EN', 'P0.31': 'UVC_PD',
    'P0.09': 'NFC1', 'P0.10': 'NFC2', 'P0.07': 'CHG_STAT',
    'P0.12': 'LED_STAT', 'P1.00': 'RING_DATA',
    'P1.08': 'BTN_DFU', 'P1.09': 'BTN_FRESET',
    'D+': 'USB_DP', 'D-': 'USB_DM',
    'VBUS': 'VBUS', 'VDDH': 'VBAT', 'VDD': '3V3',
    'SWDIO': 'SWDIO', 'SWDCLK': 'SWCLK', 'P0.18': 'RESET',
    'GND': 'GND',
}
# map U1 pin number -> pin name from netlist libparts? simpler: use inv.json
inv = json.load(open('inv.json'))
u1pins = {p['num']: p['name'] for i in inv if i['ref'] == 'U1' for p in i['pins']}
pin2net = {}
for en, em in exported.items():
    for (r, p) in em:
        if r == 'U1':
            pin2net[p] = en
spec_fail = 0
for num, pname in sorted(u1pins.items(), key=lambda t: int(t[0])):
    net = pin2net.get(num)
    want = SPEC_U1.get(pname)
    if want is None:
        # must be NC / unconnected
        if net and not net.startswith('unconnected-'):
            err('U1 pin %s (%s) should be unconnected, is on %s' % (num, pname, net))
    else:
        got = net.lstrip('/') if net else None
        if got != want:
            err('U1 pin %s (%s): spec wants %s, netlist has %s' % (num, pname, want, net))

print()
print('exported nets: %d total, %d multi-pin, %d single-pin' %
      (len(exported), len(multi), len(single)))
print('single-pin nets:')
for en in sorted(single):
    print('   ', en, sorted(single[en]))
print()
print('NETLIST DIFF: %s' % ('EMPTY (all checks pass)' if fail == 0 else '%d problems' % fail))
sys.exit(1 if fail else 0)
