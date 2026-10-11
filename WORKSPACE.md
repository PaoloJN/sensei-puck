# Workspace Guide

## Active Work Areas

| Area | Path | Purpose |
|---|---|---|
| Hardware | `hardware/` | KiCad project, board spec, fab exports, orders |
| Firmware | `firmware/` | PlatformIO (nRF52) firmware |
| Mechanical | `mechanical/` | Shell, ballast, sealing, optical shroud |
| Docs | `docs/` + root docs | Current truth: shopping list, protocols |
| Planning | `planning/` | Research context — background, may go stale |

## Active KiCad Projects

- `hardware/hardware-puck-carrier/` — spin-1 carrier board (schematic wired,
  placement revised, routing in progress; spec in `hardware/carrier-board-spec.md`,
  placement scheme in `hardware/placement-guide.md`)
- `hardware/archive/` — three milestone snapshots + retired generator script

## Current Hardware Assumptions

- Ø46 mm round 4-layer carrier (Sig/GND/PWR/Sig), ENIG, JLC-assembled both
  faces, 0402 passives. MDBT50Q-1MV2 module on the bottom face, antenna at
  the west rim with an all-layer keep-out.
- EC: four coplanar gold pads (2×8 mm) fanned on the top face east rim
  (E3/E4 force, E1/E2 sense).
- On-board I2C: MS5837 (0x76), AS7341 (0x39), FDC1004 (0x50), LSM6DSO (0x6A).
- Pin map: `hardware/carrier-board-spec.md`; also enforced by the schematic/PCB topology check.
- Enclosure concept: clear epoxy after validation and recovery gates; LiPo pouch under the board;
  magnetic dock pads on the bottom face; antenna faces DOWN over an air gap.

## Do Not Use As Active Guidance

- `planning/water-puck-research.md` product-scale sections (potting, Tritan
  molding, Qi charging, compliance costs, CR2477) — superseded by the POC
  design in `hardware/carrier-board-spec.md`. The physics/sensor sections
  remain valid.
- `docs/history/` — past reviews and the wiring guide; records, not guidance.
