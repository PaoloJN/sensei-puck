# hardware-puck-carrier — spin 1

KiCad 10 project for the Ø46 mm, 4-layer (Sig / GND / PWR / Sig) carrier.
Design truth: `../carrier-board-spec.md` (pin map, EC front end, keep-outs,
JLC order settings). Placement scheme: `../placement-guide.md`.

| File | Role |
|---|---|
| `puck-carrier.kicad_sch` | Flat single-sheet schematic, fully wired, ERC 0 errors |
| `puck-carrier.kicad_pcb` | Board: placed, keep-outs drawn, routing not started |
| `lib/` | Project symbols (`puck-extra`), footprints (`puck-parts.pretty`), 3D models |
| `LIBRARIES.md` | Symbol/footprint provenance and verification notes |
| `scripts/wiring/` | The 2026-08-31 wiring generator (reproduces that day's schematic only) |
| `renders/` | Current renders (regenerate with `kicad-cli pcb render`) |
| `analysis/` | Analyzer cache (gitignored except the manifest) |

Checklist before ordering (from CLAUDE.md):
- [ ] ERC clean, DRC clean against JLC 4-layer rules (min clearance 0.15 mm)
- [ ] Gerber render checked in the JLC viewer
- [ ] 1:1 paper print with the real MDBT50Q module placed on the footprint
- [ ] ENIG + black mask selected, assembly both faces, qty 5 / assemble 2
- [ ] Antenna sector: no copper on any layer, no parts either face

Close KiCad before running any script against these files.
