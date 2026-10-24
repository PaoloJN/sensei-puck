# Project status

**October 12, 2026 — design revision in progress; not ready to fabricate.**
No parts have been bought or hardware assembled. Budget ceiling approximately
$300, maximum two PCB spins. Historical September status is preserved in
`docs/history/2026-09-paused-baseline/`.

**2026-10-17 evening (v2 board):** 0 DRC errors, parity 0, 33 unconnected after Paolo's hand pass plus the file-mode clean-up (clearances, GND stitches, 3V3 plane re-joined, C10 flipped, FID5 moved). Blocked on decisions: (1) keep or delete TP21–TP24 (BTN_DFU/BTN_FRESET/EXP_A4/EXP_A5 pads behind the EC fingers); (2) 5V north→south needs one F.Cu slot east of the FDC — free it by moving EC_SENSE_B's F.Cu run (y 99.45) or EC_A's F.Cu diagonal to B.Cu; (3) HEATER_EN via at (139.25,105.65) is boxed by EC_DRV_HI/LO on PWR — move Q4/R12 toward the module or re-route EC_DRV_LO; (4) SHLD1 shield zone: tie to GND or accept a 0.45 mm via at 0.1 mm gaps between the FDC disc and ring. See `docs/changelog.md`.

**2026-10-16 v2 board, evening:** 0 DRC errors, parity 0, 53 unconnected after the file-mode routing pass (east column, I2C, LED pull-downs, boost corner); HEATER_EN / EC_DRV_LO / EC_DRV_HI / BOOST_EN blocked pending a placement or pin decision — see `hardware/hardware-puck-carrier-v2/routes/escape-plan.md` and `docs/changelog.md`.

**2026-10-16 pin swaps (v2 board):** pass 1: EC_SENSE_A → P0.31/AIN7 (pad 12), PDM_DATA → P1.11 (pad 4), PDM_CLK → P1.13 (pad 6), BTN_FRESET → P1.15 (pad 8). Pass 2 (escape plan): CHG_STAT → P0.04 (pad 20), BTN_DFU → P0.06 (pad 22), LED_STAT → P0.08 (pad 24), SDA → P1.09 (pad 26), LED_850 → P1.02 (pad 50), OW_DQ → P1.10 (pad 3). Pass 3 (east column, final): SDA → P0.00 (pad 17), BTN_DFU → P0.01 (pad 18), EXP_00 → P0.04 (pad 20), EXP_01 → P0.06 (pad 22), CHG_STAT → P1.09 (pad 26). C3 is a 4.7 µF 0805 moved to the module's north-west corner. Schematic, board, `variant.h` and the spec pin table are updated together; firmware must be rebuilt. v2 also carries a 0.1 mm rule area under the module (`puck-carrier-v2.kicad_dru`) and project minimums 0.1 mm / via 0.45.

## Completed revisions

- MCP73832 open-drain charger, 100 mA programming and dedicated bypass capacitors.
- Reset pulldown on boost enable; switched EC bias on P0.30.
- Correct 2.54 mm four-contact dock geometry and mating-part reference.
- Manufacturer-matched white/IR/UV LED footprints and selected inductor.
- Corrected schematic-to-PCB expansion-pin connections, moved pressure bypass,
  and marked NFC tuning capacitors DNP.
- Safe commissioning firmware startup and erased-REGOUT0 3V3 guard. All five
  PlatformIO targets compile. No hardware flashing or measurements performed.
- Current specification, purchasing plan, demonstration claims and validation
  gates reconciled; old versions archived rather than treated as completed work.

## Current checks

The schematic's last ERC run has **zero errors and four warnings**: three
single-pin labels (reserved UART_TX, UART_RX and the shield output used by the
PCB pour), and the IMU SDO/SA0 bidirectional pin tied to the ground power net.
These need to remain reviewed alongside the final release report.

The saved board has **0 DRC errors, 0 DRC warnings, 0 schematic parity
issues, and 21 unconnected items** (fresh checks on October 12). The CAD gate
is **FAIL** until those opens are closed. The checked source hashes and complete
reports are in `hardware/hardware-puck-carrier/checks/manifest.json`.

This pass connected USB D− across U11, rerouted its obstructing VBUS crossing,
connected the module's VBAT supply, bridged the remaining split 3V3 plane, and
improved ground connections. Eight starved GND pad thermals were changed to
solid connections; redundant dangling copper was removed. **369 trace corners
now use native tangent copper arcs**, verified without adding DRC errors or
opens. Full feature set, footprint positions, capacitive electrodes, antenna
keep-out and four-layer stack remain unchanged.

The remaining 21 opens are 8 GND connections and one each on EC_SENSE_A,
EC_SENSE_B, PDM_DATA, PDM_CLK, BTN_FRESET, EXP_01, EC_BIAS_EN, CHG_STAT,
IMU_INT, 5V, /LED1_K, /LED1_A and /LED3_K. A local placement/routing redesign
is still needed around the module and sensor circuitry. Electrode reshaping,
electrode relocation and bulk-capacitor relocation trials were **not adopted**:
none produced a fully connected improvement over the saved board.

The routing tools now use a project-aware KiCad copper refill and exact polygon
connectivity before raster pathfinding. Previously, a 0.0347 mm gap between
3V3 pour pieces was smaller than the routing grid and was falsely reported as
connected. DRC remains the authoritative connectivity check.

Current previews: [top](hardware/hardware-puck-carrier/renders/october-rounded-top.png)
and [bottom](hardware/hardware-puck-carrier/renders/october-rounded-bottom.png).
These are design previews. **The PCB is not finalized or ready to fabricate;
no fabrication release has been generated.**

## Remaining work

1. Finish routing with original physical rules, refill zones, inspect all copper,
   and pass DRC with zero unconnected items and zero schematic mismatch.
2. Finish exact assembly BOM, rotation/land-pattern review, and obtain an itemized
   two-sided assembly quote that respects the total budget.
3. Check a 1:1 footprint print against the actual module and dock mate before an order.
4. Implement the custom bootloader and raw sensing/logging application; commission
   an unsealed board using references and current-limited power.
5. Validate RF, leakage, charging, optical shroud, seals and recovery from a
   crashing application before permanent sealing.

Start with [engineering review](docs/engineering-review-2026-10.md),
[board spec](hardware/carrier-board-spec.md), and
[validation plan](docs/validation-plan.md).
