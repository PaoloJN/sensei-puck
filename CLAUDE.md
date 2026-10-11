# Water Puck — Working Conventions

College proof-of-concept: a drop-in BLE water sensor puck. One-off build, not
a product. Read `STATUS.md` first for current state; `WORKSPACE.md` for the
area map. Structure mirrors `~/Projects/openchess`.

## Hard Constraints

- Budget ceiling ~$300 personal money; max 2 PCB spins. Never propose
  spending that ignores this.
- The carrier is JLC-assembled on BOTH faces (0402 passives, LGA/OLGA sensors
  on board). Hand-placed only: U1 module, U5, J1, piezo/battery/NFC wires.
- The two project rules, non-negotiable:
  1. **Store raw sensor data** (counts + the acquisition settings that
     produced them), never derived values. Calibration applied downstream.
  2. **No number without a reference** — every EC/temp reading validated
     against standards (homemade KCl) or campus lab instruments.
- Never claim the device assesses water *safety*. Freshness score, anomaly
  detection, liquid classification only.

## Technical Decisions (settled — don't relitigate without new evidence)

- Brain: Raytac MDBT50Q-1MV2 bare nRF52840 module on a Ø46 mm 4-layer carrier
  (the XIAO nRF52840 Sense is the bench mule only). Firmware: PlatformIO +
  Adafruit nRF52 core, custom `mdbt50q_puck` variant, BLE OTA DFU via a custom
  Adafruit bootloader build.
- Antenna radiates DOWN through container base from a dry air cavity;
  store-and-forward + tilt-triggered sync. Glass/plastic containers only.
- EC: gold ENIG PCB fingers, bipolar AC excitation from GPIO, two-resistor
  auto-ranging (1 kΩ / 100 kΩ), differential ADC. No steel pins, no DC, no
  AD5933.
- Clear epoxy dip after the commissioning gates (2026-08-31, supersedes the
  serviceable O-ring shell); magnetic dock pads for charge + USB; BLE OTA DFU is
  the only reflash path after the dip. See `docs/decisions.md`.
- Pin map lives in `hardware/carrier-board-spec.md` — update it and STATUS.md
  when anything changes.

## Workflow

- Close KiCad before running any hardware scripts or exports.
- Before any JLCPCB order: ERC + DRC, Gerber render check, 1:1 paper
  footprint check with the real MDBT50Q module on top.
- History lives in git. No `.pre-*` / `.orig` / `.bak` snapshot files in the
  tree (they are gitignored); decisions go in `docs/decisions.md`, dated work
  log in `docs/changelog.md`.
- DFU round-trip must be proven before the shell is sealed.
