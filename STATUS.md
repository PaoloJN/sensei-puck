# Project status

**October 11, 2026 — design revision in progress; not ready to fabricate.**
No parts have been bought or hardware assembled. Budget ceiling approximately
$300, maximum two PCB spins. Historical September status is preserved in
`docs/history/2026-09-paused-baseline/`.

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

PCB routing is unfinished but far along (2026-10-11 night, see
`docs/changelog.md`): the saved board has **0 DRC errors, 0 schematic parity
issues, 28 unconnected items** = 15 signal connections, 12 GND pour islands and
1 3V3 plane island. Everything else is routed (planes, fan-out, ring, boost,
local nets, most module crossings). The 15 signals are boxed in by the module's
east pad column under the FDC no-via zone; every automated strategy tried
(Freerouting rounds, grid A* with rip-up, regional and whole-net re-routes,
pins moved to spare pads, FDC pads shifted in simulation) plateaus there. The
remaining options are interactive push-and-shove in KiCad or a re-plan of the
bottom-layer area under the FDC pads (reserve it for local nets, define escape
channels, re-route). **No candidate is fabrication-approved, and no new
fabrication release has been generated.**

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
