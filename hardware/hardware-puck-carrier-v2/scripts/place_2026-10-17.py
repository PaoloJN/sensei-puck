"""Placement pass 2026-10-17 (file mode, KiCad closed): optical LED block.
Q1 rotated 180 (gate pad top-right, fed from module pad 39 on B.Cu). D1 and D3 move next to D2
in the empty south-east of the top face so every LED net gets vias from the bottom-side pocket
under U7. R5/R6/R7 (5V -> LED anode) flip to the top face beside their LEDs, fed from the 5V
top-side rail. KiCad python: place_2026-10-17.py board.kicad_pcb ; re-copy the .kicad_pro after.
"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
def mm(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
# ref: (x, y, rot, layer)
# second pass: courtyards clear of D2/D1/each other and of the EXP_00 via; final positions
moves = {'Q1': (139.6, 107.8, 180, 'B'), 'D3': (153.5, 111.95, 90, 'F'), 'D1': (157.3, 110.1, 0, 'F'),
         'R5': (160.5, 110.5, 90, 'F'), 'R6': (159.4, 103.7, 270, 'F'), 'R7': (155.7, 112.5, 180, 'F')}
for ref, (x, y, rot, layer) in moves.items():
    fp = b.FindFootprintByReference(ref)
    want = pcbnew.F_Cu if layer == 'F' else pcbnew.B_Cu
    if fp.GetLayer() != want:
        try: fp.SetLayerAndFlip(want)
        except Exception as e: fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT if hasattr(pcbnew, 'FLIP_DIRECTION_LEFT_RIGHT') else False)
    fp.SetPosition(mm(x, y)); fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        print(f"{ref}.{p.GetNumber():<2} {p.GetNetname():<12} {b.GetLayerName(fp.GetLayer())} x {pcbnew.ToMM(bb.GetLeft()):.2f}-{pcbnew.ToMM(bb.GetRight()):.2f} y {pcbnew.ToMM(bb.GetTop()):.2f}-{pcbnew.ToMM(bb.GetBottom()):.2f}")
pcbnew.SaveBoard(sys.argv[1], b); print('saved')
