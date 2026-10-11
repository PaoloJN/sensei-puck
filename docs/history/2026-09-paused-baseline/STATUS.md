# Project Status

Snapshot as of **2026-09-04**. History: `docs/changelog.md`. Decisions:
`docs/decisions.md`.

## Intent

One-off college proof of concept. One reliable puck that demos great, not a
product. Max 2 PCB spins, ~$300 ceiling, campus labs for tools/calibration.

## Canonical references

| Reference | Role |
|---|---|
| `hardware/carrier-board-spec.md` | Design truth: pin map, power, EC front end, keep-outs, commissioning gates, JLC order |
| `hardware/placement-guide.md` | The polar placement scheme actually on the board (numbers) |
| `hardware/hardware-puck-carrier/` | KiCad 10 project (sch + pcb + libs); `LIBRARIES.md` for provenance |
| `docs/shopping-list.md` | Off-board parts, tools, shell (~$180 core) |
| `docs/decisions.md` / `docs/changelog.md` | Dated decisions / dated work log |
| `docs/history/` | Past reviews (2026-08-31 design review, net review, wiring guide) — records only |
| `firmware/README.md` | Firmware status, milestones, build notes |

## Current state

| Area | State |
|---|---|
| Research | Done — sensors final, RF strategy decided, market validated |
| Design review | Done 2026-08-31 (5 critical / 15 major, all fixed) |
| Schematic | Wired, 115 symbols (expansion pads TP23–TP26, DFU pads TP21/TP22, aux pads E5/E6 added 2026-09-04), ERC 0 errors (3 accepted single-pin warnings: UART_TX/RX, SHLD1). UVC pins NC, D5 excluded from board |
| Board | Ø46 4-layer, 120 footprints, placed to the polar scheme. **Routing started 2026-09-04**: planes + guards + pull-backs drawn, net classes/widths set, module escapes, boost loop, full LED ring, electrode/FDC vias pre-routed by script. DRC 0 errors, parity clean, **127 connections left — Paolo hand-routes** (order in `hardware/placement-guide.md` → Routing). Freerouting rejected (stalls at ~60 unrouted on the 0.6×0.4 mm module pads) |
| Feature set | **FROZEN for spin 1 (2026-09-04)** — see `docs/decisions.md`. No UVC, no probes, no more sensors. NFC = solder option (off-board coil). Routing can start |
| Build risks (watch these) | (1) Hand-soldering the 61-pad MDBT50Q module — check whether JLC stocks it at order time and let them place it. (2) U5 MS5837 LGA hand-placed with hot air, gel port must stay clean (U6 is now µSOP, JLC-placed). (3) Epoxy dip is one-way: build 2 boards, dip only the second after the naked one passes every gate. (4) NFC coil tuning after assembly — skip NFC entirely if it eats more than a day. (5) Custom bootloader + UICR REGOUT0 before anything else |
| Parts | **NOT ORDERED — still the critical path** |
| Firmware | PlatformIO skeleton + bench sketches; `mdbt50q_puck` variant builds; app not started |
| Mechanical | Epoxy dip after commissioning; shell ledge/preload for the board; nothing bought |
| Repo | Cleaned 2026-09-04; **no git commit yet** — make the first one |

## Next actions (in order)

1. **Order parts** — DigiKey: MDBT50Q-1MV2, MS5837-02BA, DS18B20+, TPS61023,
   LSM6DSO, IM69D130, XC6206P182MR, AS7341, FDC1004, LEDs (verify true 365 nm),
   passives per the spec parts list.
2. Finish feature edits (Paolo), then Update PCB from Schematic once in the GUI
   (copies 11 description fields; nothing else should change).
3. Hand-route the remaining 127 connections in the order in `hardware/placement-guide.md` → Routing; refill zones, DRC, more GND stitching vias.
4. Bench-validate the EC front end against the homemade KCl standard before
   routing is final.
5. 1:1 paper check with the MDBT50Q land pattern; ERC/DRC + Gerber render;
   JLC order (4-layer, ENIG, black mask, assembly both faces, qty 5 / asm 2).

## Commissioning gates (before the epoxy dip)

- Custom bootloader build only (`USE_NFCT = yes`, nice!nano base) — never a
  prebuilt hex; `nrfjprog --memrd 0x1000120C` == `0xFFFFFFFF`.
- UICR REGOUT0=3V3 written (`nrfjprog --memwr 0x10001304 --val 5`) and the
  rail measures 3.3 V; re-check after any eraseall.
- Sleep-during-charging in place (MCP73831 has no power path).
- **BLE DFU round-trip proven incl. app-initiated OTA** — the only reflash path
  after potting.
