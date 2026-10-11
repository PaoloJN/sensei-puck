"""Apply the October electrical corrections to the existing schematic.

Run once with KiCad closed. Idempotent additions; preserves existing UUIDs.
PCB synchronization is handled by sync_board.py using an exported netlist.
"""
from pathlib import Path
import copy
import sys
import uuid

sys.path.insert(0, str(Path(__file__).parent / 'wiring'))
from sexp import parse, find, find_all, atom, serialize, Sym

PROJECT = Path(__file__).resolve().parents[1]
STOCK = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')

def pretty(n, depth=0):
    if not isinstance(n, list):
        return serialize(n)
    if not any(isinstance(v, list) for v in n):
        return serialize(n)
    first = next(i for i, v in enumerate(n) if isinstance(v, list))
    return '(' + ' '.join(serialize(v) for v in n[:first]) + '\n' + '\n'.join(
        '\t' * (depth+1) + pretty(v, depth+1) for v in n[first:]
    ) + '\n' + '\t' * depth + ')'

def prop(n, key, value=None):
    p = next((p for p in find_all(n, 'property') if atom(p[1]) == key), None)
    if value is None:
        return atom(p[2]) if p else ''
    if p is None:
        p = parse('(property "X" "" (at 0 0 0) (hide yes) (effects (font (size 1.27 1.27))))')[0]
        p[1] = ('str', key)
        n.append(p)
    p[2] = ('str', value)

def main():
    path = PROJECT / 'puck-carrier.kicad_sch'
    root = parse(path.read_text())[0]
    syms = {prop(s, 'Reference'): s for s in find_all(root, 'symbol')}
    libs = find(root, 'lib_symbols')
    stock = parse((STOCK / 'symbols/Battery_Management.kicad_sym').read_text())[0]
    charger = copy.deepcopy(next(s for s in find_all(stock, 'symbol') if atom(s[1]) == 'MCP73832-2-OT'))
    charger[1] = ('str', 'Battery_Management:MCP73832-2-OT')
    if not any(atom(s[1]) == atom(charger[1]) for s in find_all(libs, 'symbol')):
        libs.append(charger)
    find(syms['U7'], 'lib_id')[1] = charger[1]
    for key in ('Datasheet', 'Description'):
        prop(syms['U7'], key, prop(charger, key))
    prop(syms['U7'], 'Value', 'MCP73832T-2ACI/OT')
    prop(syms['R17'], 'Value', '10k')  # 100 mA: lower heat in sealed assembly
    prop(syms['D1'], 'Value', '67-21/T2C-ZV1W2E/2T')
    prop(syms['D2'], 'Value', 'HIR67-21C/L11/TR8')
    for ref in ('D1', 'D2'):
        prop(syms[ref], 'Footprint', 'puck:LED_Everlight_67-21_PLCC2')
    prop(syms['D3'], 'Value', 'VLMU1610-365-135')
    prop(syms['D3'], 'Footprint', 'puck:LED_Vishay_VLMU1610')
    prop(syms['D3'], 'Datasheet', 'https://www.vishay.com/docs/84374/vlmu1610-365-135.pdf')
    prop(syms['L1'], 'Value', 'SWPA4030S1R0NT')
    prop(syms['L2'], 'Value', 'NFC external coil OPTION')
    # Actual coil is selected and tuned with the assembled mechanical stack.
    for ref in ('C12', 'C13'):
        prop(syms[ref], 'Value', 'DNP tune NFC C0G')
        find(syms[ref], 'dnp')[1] = Sym('yes')
    sheet_id = atom(find(root, 'uuid')[1])
    # Avoid permanently biasing wet EC pads against the exposed dock ground.
    # R20 is fed by a spare low-frequency GPIO, low/Hi-Z between acquisitions.
    for label in find_all(root, 'global_label'):
        at = find(label, 'at')
        if abs(float(at[1])-386.08)<0.001 and abs(float(at[2])-207.01)<0.001:
            label[1] = ('str', 'EC_BIAS_EN')
    for nc in list(find_all(root,'no_connect')):
        at=find(nc,'at')
        if abs(float(at[1])-43.18)<0.001 and abs(float(at[2])-66.04)<0.001:
            root.remove(nc)
            root.append(parse(f'(wire (pts (xy 43.18 66.04) (xy 40.64 66.04)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))')[0])
            root.append(parse(f'(global_label "EC_BIAS_EN" (shape passive) (at 40.64 66.04 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "{uuid.uuid4()}"))')[0])
    for ref, template, x, y, value, footprint, top, bottom in (
        ('C24', 'C10', 452.12, 45.72, '10uF 16V X7R', 'Capacitor_SMD:C_1206_3216Metric', 'VBUS', 'GND'),
        ('C25', 'C10', 474.98, 45.72, '10uF 16V X7R', 'Capacitor_SMD:C_1206_3216Metric', 'VBAT', 'GND'),
        ('R33', 'R17', 452.12, 73.66, '100k', 'Resistor_SMD:R_0402_1005Metric', 'BOOST_EN', 'GND'),
    ):
        if ref in syms:
            prop(syms[ref], 'Value', value)
            prop(syms[ref], 'Footprint', footprint)
            if ref in ('C24','C25'):
                prop(syms[ref], 'Description', 'TDK C3216X7R1C106K160AC; minimum 4.7uF effective at operating bias')
                prop(syms[ref], 'Datasheet', 'https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X7R1C106K160AC')
            continue
        s = copy.deepcopy(syms[template])
        at = find(s, 'at'); dx, dy = x-float(at[1]), y-float(at[2])
        at[1:] = [Sym(str(x)), Sym(str(y)), Sym('0')]
        for p in find_all(s, 'property'):
            pa = find(p, 'at')
            pa[1] = Sym(str(round(float(pa[1])+dx, 4)))
            pa[2] = Sym(str(round(float(pa[2])+dy, 4)))
        find(s, 'uuid')[1] = ('str', str(uuid.uuid4()))
        for p in find_all(s, 'pin'):
            find(p, 'uuid')[1] = ('str', str(uuid.uuid4()))
        s.remove(find(s, 'instances'))
        s.append(parse(f'(instances (project "puck-carrier" (path "/{sheet_id}" (reference "{ref}") (unit 1))))')[0])
        prop(s, 'Reference', ref); prop(s, 'Value', value); prop(s, 'Footprint', footprint)
        prop(s, 'Description', '2026-10 reliability correction')
        root.append(s)
        # Both stock Device:C and Device:R use pins at +/-3.81 mm on the Y axis.
        for net, sign in ((top, -1), (bottom, 1)):
            py, ly = round(y+sign*3.81, 4), round(y+sign*6.35, 4)
            root.append(parse(f'(wire (pts (xy {x} {py}) (xy {x} {ly})) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))')[0])
            root.append(parse(f'(global_label "{net}" (shape passive) (at {x} {ly} {90 if sign == -1 else 270}) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uuid.uuid4()}"))')[0])
    path.write_text(pretty(root)+'\n')

if __name__ == '__main__':
    main()
