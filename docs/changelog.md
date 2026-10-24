# Changelog

Dated work log, newest first. Moved out of STATUS.md on 2026-09-04; the
2026-08-31 / 09-01 entries are the original STATUS table cells, verbatim.

## 2026-10-17 evening — v2: hand routing reviewed, clearance fixes, 3V3 plane re-joined

Paolo routed by hand in KiCad (two sessions, 01:29–02:20 and 20:40–21:51): R1/R2 moved to y 94.26, R3/R4 beside the FDC, I2C trunk straight across PWR, EC_DRV_HI/LO, SWD, NFC, PIEZO, RING_DATA, LED anodes/cathodes, PAD_DP/DM, PZ_DRV, 1V8, EC_NODE_D, VBAT north, TP21–26 re-spaced; FID1/FID2 deleted. Board at hand-over: 38 unconnected, 10 DRC errors.

File-mode pass afterwards (`routes/fix-2026-10-17-evening*.json`, `gnd-3v3-*.json`, `3v3-links-*.json`, `3v3-south-*.json`, `south-fixes-*.json`, `led850-gate-*.json`):
- Nine clearance errors fixed by 0.05–0.1 mm via moves (RING_DATA, SDA, 3V3, EC_SENSE_B, BTN_FRESET); FID5 to (136.5,112.3) on its keepout circle, out of ANTENNA_KEEPOUT.
- GND stitch vias at Q3.2, Q1.2, U10.1; C10 rotated 180° so its GND pad meets the top pour.
- The PWR_3V3_IN2 pour had been cut into four pieces by the PWR rows. Re-joined on copper: U1.28 and U8 on B.Cu to the C17 via around the west of U4; the south pour fed by an F.Cu rail from the (154.9,101.15) via east of U3 to a via at (157.6,105.55). The dead EXP_00 F.Cu spur and its via at (154.0,103.5) were removed to make room. 3V3 is one net again.
- LED_850 gate trace re-routed down the Q2.1/Q2.3 gap (0.1 mm module rule) so the pour between Q1.2 and Q2.2 is continuous.

Result: 0 DRC errors, 20 warnings, parity 0, 33 unconnected. Open: 5V ×4, GND ×3 (Q2.2, U1.33, one pour pair), SCL ×3, SDA ×3, EXP_A4 ×2, VBAT ×2, EC_A, EC_SENSE_A, 1V8, EXP_A5, PDM_DATA, PDM_CLK, /RING_D0, OW_DQ, EC_B, RESET, HEATER_EN, PIEZO, IMU_INT, BOOST_EN, NFC1, /PAD_DM.

Finding: with the PWR row band (y 95.95–99.65), the USB/VBUS/VBAT/EXP_01 runs on B.Cu and the EC_A / EC_SENSE_B / LED2_K / CHG_STAT runs on F.Cu, the board has no remaining north–south crossing in the x 137–169 band except the one F.Cu slot east of U3 now used by 3V3. 5V (boost → LED resistors) and HEATER_EN cannot be completed without re-routing one of those; SHLD1 (FDC shield zone) has no legal via spot (0.65 mm gap between disc and ring). Decisions listed in STATUS.md.

## 2026-10-17 — v2: optical LED block re-placed, pin pass 4, south-west copper reset

- Root cause of the south-west stall: the three LED drains and three anode nets (D1–D3 on the top face, east; Q1–Q3 and R5–R7 on the bottom, south-west) had no copper and no route, and D3 at (159.7,100) had no via access at all. Paolo: "feel free to move stuff as long as the pcb will look good at the end".
- Placement (file mode, `scripts/place_2026-10-17.py`): Q1 rotated 180° (gate pad top-right, fed straight from the module); D1 → (157.3,110.1) under D2; D3 → (153.5,111.95) rot 90 left of D1; R5/R6/R7 flipped to the top face at (160.5,110.5)/(159.4,103.7)/(155.7,112.5) next to their LEDs and the 5V top rail; the old bottom-side 5V bus, its via and top diagonal removed.
- Pin pass 4: pad 37 → LED_850 (P0.13), pad 39 → LED_WHITE (P0.15), pad 41 stays HEATER_EN (P0.17), pad 48 → LED_365 (P0.24), pad 50 → UART_TX (P1.02). Schematic labels and board pad nets updated; `variant.h` / spec table still to follow.
- Copper reset south of the module (`routes/sw-cleanup.json`, `se-prep.json`, applied with the new `cl route --allow-opens`): old LED_WHITE/LED_850/LED_365/HEATER_EN routes, the VBAT PWR diagonal + bottom branch + top rail (replaced by a bottom link U7.3 → C25 at y 111.5), nine GND stub vias whose pads keep the bottom pour (Q1.2, Q2.2, Q3.2, pad 33, C10.2, U10.1, D8.1, U7, R17.2, Q4.2), the U5.2 3V3 via moved to (139.0,108.7), CHG_STAT moved to a top-side column. Gates routed: LED_WHITE pad 39 → Q1.1, LED_850 pad 37 → Q2.1, LED_365 pad 48 → Q3.1 (`routes/gates.json`).
- Board: 0 errors, 6 warnings, parity 0, 61 unconnected. Still open and planned (not applied): VBAT via the north band (`routes/escape-plan.md`), the four-net PWR band, the LED cathode/anode nets in the south-east pocket — handed to Paolo for push-and-shove routing in KiCad.

## 2026-10-16 — v2 routing: GND tidy, 3V3 fan-out, 5V ring, pin swap, module rule area

- New copy `hardware/hardware-puck-carrier-v2/` routed from scratch with CopperLoop (`~/Projects/copperloop`, live IPC edits, kicad-cli gate).
- GND: one stub + one via per pad (81 redundant pieces removed). 3V3: via per pad, trunk under the FDC disc to C3/C17/U8/C9.
- 5V LED ring: rounded arcs on F.Cu at r 19.45, steps out to r 22 past the EC finger tips, fed from D9 through one via; ten fan-out vias moved out of its lane. Firmware rule: LEDs off during EC measurement.
- Pin swaps for module escapes, pass 1: EC_SENSE_A → P0.31 (pad 12), PDM_DATA → P1.11 (pad 4), PDM_CLK → P1.13 (pad 6), BTN_FRESET → P1.15 (pad 8). Pass 2, from the escape plan (`hardware-puck-carrier-v2/routes/escape-plan.md`): CHG_STAT → P0.04 (pad 20), BTN_DFU → P0.06 (pad 22), LED_STAT → P0.08 (pad 24), SDA → P1.09 (pad 26), LED_850 → P1.02 (pad 50), OW_DQ → P1.10 (pad 3). `variant.h`, spec table, STATUS updated. Pass 3: SDA → P0.00 (pad 17), BTN_DFU → P0.01 (pad 18), EXP_00 → P0.04 (pad 20), EXP_01 → P0.06 (pad 22), CHG_STAT → P1.09 (pad 26), so SCL, SDA and BTN_DFU leave the module northward and the other four take the south lane.
- C3 → 4.7 µF 0805 relocated to (139.3, 91.5) next to U9; R17 to the old R31 spot north of U7; D8/R31 shifted; R11 0.4 mm west. The corridor between the module and the FDC is free of power feeds.
- Rule area MODULE_RULES (B.Cu, x 137.4–146.2, y 93.4–106.6) with `.kicad_dru`: 0.1 mm trace/clearance (EC nets 0.15); project minimums 0.1 mm, via 0.45 / 0.2 hole (JLC 4-layer 0.09).
- Board state: 0 DRC errors, parity 0, 109 unconnected (all signals), power and planes complete.
- Evening, KiCad closed, file mode (`cl route SPEC --board FILE --apply`, scratch copy + kicad-cli gate, board copied back only on PASS): pull-ups R1/R2 moved to (157.4/156.3, 96.4) with a shared 3V3 via; I2C north (U4.9/U4.10 vias, PWR runs to the lane via and U3.8); east column — SCL/SDA up the C3 corridor onto PWR rows y 94.35/92.95, EXP_00/EXP_01/LED_STAT/CHG_STAT down 0.1 mm columns x 144.45–145.35 into 0.1 mm lane rows y 102.95–103.85, staircase vias at x 153.3–154.75, PWR to TP25/TP26 (back on B.Cu at x 157.7/158.4), R31.1 and U7.1; LED pull-downs R8/R9/R10 (LED_WHITE around the fiducial keepout and under the ring, LED_850 via at (140.0,113.6), LED_365 on B.Cu); SCL PWR column at x 155.55 cut back to y 97.2 with an F.Cu stub from the R2.2 via into U3.2 (frees the PWR layer east of the FDC between y 97.6 and 102.6); VBAT via west of U2 moved to (155.5,89.15) so U2.2 can exit; BOOST_EN U2.2 ↔ R33.1 via a PWR hop; HEATER_EN Q4.1 ↔ R12.1. Specs in `routes/` (pullups, i2c-north, east-column + gen, leds, scl-rework, east-links). Board: 0 errors, 4 warnings, parity 0, 53 unconnected (was 67).
- Blocked, needs a decision: HEATER_EN (41), EC_DRV_LO (46), EC_DRV_HI (45), BOOST_EN (44) from the module south row. The module has a third pad column (56–61, x 136.55–137.15, y 97.8–102.2), so there is no legal via spot under the body for four nets at 0.3 pitch, and the hand-routed LED_850 (PWR y 104.95) and LED_WHITE (PWR L at x 140.6 / y 107.55) plus the Q1/Q2/Q3 GND vias fence the PWR south band. Draft kept in `routes/sw-bundle-draft.json` (east halves are valid). Options in `routes/escape-plan.md`.

## 2026-10-12 — rounded copper and verified connectivity fixes, 28 → 21 opens

- Saved PCB: **0 DRC errors, 0 DRC warnings, 0 parity issues, 21 opens**
  (13 signal/power connections and 8 GND connections). ERC: 0 errors / 4 warnings;
  independent netlist topology checks: 0 errors. Fresh source-hashed reports
  replace the stale reports in `hardware/hardware-puck-carrier/checks/`.
- Connected `/PAD_DM` between U11's two D− pins; moved the blocking VBUS section
  through two vias. Connected U1's VBAT supply, added ground links, repaired
  eight starved ground-pad thermals with solid connections, and removed dangling
  stubs/vias. Subsequent refills were checked for newly isolated copper.
- Connected the remaining 3V3 plane split with a short 0.3 mm bridge and a
  0.5/0.3 mm via. The previous raster connectivity model merged two copper
  polygons across a **0.0347 mm physical gap**; exact geometry found two islands.
  The bridge removed the actual KiCad unconnected item.
- Rounded **369 corners** with native KiCad copper arcs (approximately
  0.06–0.45 mm radius). Preserved widths, nets and layers; skipped junctions and
  constrained corners. Refill DRC and parity passed; rounding did not add opens.
  Added `scripts/round_corners.py`; regenerated top/bottom design previews.
- Corrected `geom_export.py` to refill a disposable board/project copy using
  KiCad CLI rules, preserve source files, export pad-local clearance and record
  the source hash. Corrected `grid_router.py` to determine islands using polygon
  intersections before rasterization and respect exported pad-local clearances.
- Rejected scratch trials: a C-shaped FDC ring (24% less sensing copper), moving
  the full FDC pair north with nearby parts/test pads relocated, and moving C3
  to free the module escape area. They did not yield a fully connected, better
  verified board; **none of these geometry/placement changes reached the saved
  PCB**. The relocation trial's Freerouting view also reported pre-existing
  model violations; it was stopped and not imported. Scratch files are under
  `/private/tmp/sensei-final-12/`, not a fabrication source.
- All original features and component positions retained. No signal routing
  added on the In1 ground plane. No parts ordered, no new fabrication package,
  and no hardware or firmware measurements. The remaining 21 opens must still
  be fixed; this is a verified improvement, **not PCB completion**.

## 2026-10-11 (night) — Codex limit-out, grid router, 49 → 28 unconnected

- Codex's evening session ("fix the pcb… round traces") ran 234 repair iterations in `/private/tmp/sensei-pcb-finish` and stopped on its usage limit at 20:15 with no report. Its last candidate (`clean11.kicad_pcb`: 33 unconnected, 0 errors) was **not** adopted: it routes SDA, EXP_00, HEATER_EN, SWCLK, EC_BIAS and the LED1 nets on the In1 ground plane, removed the module 3V3 trunk and ripped up the module escapes (SCL ×4, SDA ×3, VBUS, USB_DM, NFC2, RING_DATA open). Nothing from it reached the repo.
- Repo board now: **0 DRC errors, 0 parity issues, 28 unconnected** = 15 signals, 12 GND pour islands, 1 3V3 island (was 49). Changes: 3V3 trunk under the module moved (`U1-28` now fed through U8/C9 instead of the x=144.3 wall that blocked pads 18–26), EC_A→TP6 and EC_BIAS (R22→R23) routed, nine 3V3 plane pieces bridged, 16 GND islands stitched/joined, one 3V3 join on In2.
- New tools (`scripts/`): `geom_export.py` (board copper → JSON), `grid_router.py` (A* on a 0.05 mm raster, two outer layers + optional In2, KiCad pair clearances incl. EC/EXP_A4/A5 at 0.2 mm, island-to-island, optional rip-up), `apply_plans.py` (textual rip + `routelib` collision check), `gnd_stitch.py` (via per orphan pour island, prints the pads on each), `plot_region.py` (labelled window plots), `strip_region.py` / `strip_nets_region.py`, `router/riploop.sh`, `pin_swap.py` (moves EC_SENSE_A/PDM_DATA/PDM_CLK/BTN_FRESET to pads 12/4/6/8 in schematic + board; written and verified with parity, **not applied**).
- What failed, so nobody repeats it: grid rip-up loop (diverges: 49 → 99); Freerouting with everything protected (0 progress); regional strip then Freerouting (62); whole-net strip of both choke regions then Freerouting (60 / 52 with In2); hard-nets-first on the empty board then Freerouting (74 / 76 with the pin swap); FDC pads shifted 2–2.5 mm east in the model (no change — the outer layers around the module are already full). Freerouting does not count protected wiring as connectivity, so partial rip-ups of a net never complete.
- Root cause, measured: the module's outer east column (pads 15–33, x 143.45, 0.4 mm gaps) can only leave eastwards on B.Cu under the FDC pads where no via may exist; the channel to C3 is 1.35 mm (two tracks), the north lane C17/C3 2.2 mm, and Freerouting used the whole area as a highway, which also fragments the GND pour under the FDC (U1-15, U8, C3/C17, C9/R21 GND pads are on orphan islands). Fix needs a re-plan of that area, not more autorouting.
- Still open: EC_SENSE_A, EC_SENSE_B, PDM_DATA, PDM_CLK, BTN_FRESET, EXP_01, VBAT (U1-30), EC_BIAS_EN, CHG_STAT, IMU_INT, 5V (D9→R11), /LED1_K, /LED1_A, /LED3_K, /PAD_DM, 1 3V3 join (C17 stub), 12 GND islands (listed by `gnd_stitch.py`).

## 2026-10-11 (evening) — scripted routing pass, 130 → 19 signal opens

- Board taken from Codex's pre-stitch copy (130 unconnected, 23 DRC warnings) to a candidate with **0 DRC errors, 49 unconnected**: 19 signal connections, 21 GND pour islands, 9 3V3 plane islands (In2 now carries signal traces, so the 3V3 pour is no longer one piece). 1012 → ~1600 track items. Renders `renders/october-routed-{top,bottom}.png`.
- Method (`scripts/router/README.md`): 3V3 fan-out vias by script (`fanout_planes.py`, KiCad shape collision), hand routes under the FDC pads (`route_manual.py`: /CIN2 moved to the east side of U8, U8/C3/U1-28 3V3 on B.Cu to vias outside the sense pads, U4-7/U4-8 vias), then Freerouting 2.5.0 on a "router view" (`router_export.py`: fills dropped, outer-layer keep-outs only, wiring protected, complete nets hidden, widths capped 0.25 mm, In2 routable) in rounds (`round.sh`).
- Findings: Freerouting cannot drop a via anywhere under the FDC disc/ring (r ≈ 6.45 mm around 148.4,100), the module's inner-row escape vias sit 0.45 mm from the ring on F.Cu, and the only exits are the two corridors past U9 and U5. Routing the module crossings first on the empty board with In2 open was the single biggest win (crossings 36 → 6 open); every other variant plateaued at 35–48. Freerouting does not count protected wiring as connectivity (reports ~40 phantom opens), ignores `class_class` clearance, and with neck-down on emits 0.1 mm tracks.
- Still open (coordinates in the DRC report): EC_A→TP6, EC_SENSE_A ×2, EC_SENSE_B ×2, /LED1_K, /LED1_A, /LED3_K, PDM_DATA, PDM_CLK, VBAT (U1-30→U7), 5V (D9→R11), EC_BIAS (R22-1→R23-1), EC_BIAS_EN, EXP_01, CHG_STAT, BTN_FRESET, IMU_INT, /PAD_DM (U11 pins 1↔6). Each is boxed in by earlier router traces; finishing needs interactive push-and-shove in KiCad or a re-route of the EC sector by hand, plus GND/3V3 island repair.
- Not touched: placement, the LED ring, boost loop, electrode stubs, escape vias, net classes.

## 2026-10-11 — Codex revision pass (unfinished), baseline commit

- Codex (GPT-6, `codex-tui` 0.162.1) session 2026-10-10 19:34 → 2026-10-11 02:02, ended on an OpenAI usage limit mid-routing; no wrap-up. Brief: fix real-life issues, finalize the PCB, keep the full feature set.
- Schematic: U7 → MCP73832T-2ACI/OT (open-drain STAT; MCP73831 STAT can rise to VIN), R17 → 10 kΩ (~100 mA); C24/C25 10 µF/16 V X7R **1206** bypass on VBUS/VBAT; R33 100 kΩ pulldown on boost EN; R20 EC mid-rail bias fed from new `EC_BIAS_EN` on P0.30 (Hi-Z idle, no DC on wet electrodes vs dock GND); C10 moved beside U5; C12/C13 DNP; D3 generic `UV365` → Vishay VLMU1610-365-135 (same UV-A channel, real footprint); D1/D2 white/IR → Everlight PLCC2 lands; expansion-pad nets resynced to the schematic. ERC 0 errors / 4 warnings.
- Dock: CP1–CP4 pitch 4.5 → 2.54 mm, order GND, D+, D−, +5V; mate Adafruit 5358.
- Firmware: safe startup pin states, erased-only REGOUT0 3V3 guard in `initVariant`, new `bench_ec` env; all five PlatformIO targets build. Nothing flashed.
- Docs: `docs/engineering-review-2026-10.md`, `docs/validation-plan.md` new; STATUS/spec/shopping-list/product-story rewritten, September versions kept in `docs/history/2026-09-paused-baseline/`.
- Board: Freerouting 2.5.0 candidates tried; best run 41 violations / 69 unconnected / 0 parity (in Codex's scratch dir only). Saved board = its pre-stitch copy: 294 segments, 60 vias, 140 footprints, 23 violations, **130 unconnected**. Routing is NOT finished. Codex scratch dir (router inputs/outputs, DRC JSONs, untouched starting tarball) copied to `~/Projects/sensei-cup-codex-review-2026-10-11/`.
- Verified: the starting board and the 2026-09-04 archive both have 0 track segments — the September scripted pre-route was never saved, so Codex discarded nothing.
- Open for Paolo: C24/C25 as 1206 breaks the 0402-only passives decision (0603 10 µF/10 V X5R or 0805 10 µF/16 V would still meet the ≥4.7 µF effective requirement). Decide before ordering.
- First git commit of the whole tree as baseline (previous repo state had no commits).

## 2026-09-05 — symmetric sensor face

- Top face re-placed symmetric about the axis (see placement guide); FDC2 became a ring concentric with the FDC1 disc (a second disc collided with the module escape-via field); U6 swapped to DS18B20U+ µSOP-8 on the top (footprint pads renumbered to the TO-92 symbol; symbol value updated); fourth fiducial added; dip-mask outlines on Eco1.User.
- Pre-route re-run on the new placement (FDC2 via/route moved). DRC 0 errors.

## 2026-09-04 (night) — routing start

- Net classes with widths (0.2 signal / 0.25 EC + ring / 0.35 LED current / 0.4 power / 0.5 boost) in the project file.
- Planes: GND In1 with SHLD1 guard islands under the FDC pads, 3V3 In2, GND fills both faces; pull-backs under the electrodes and FDC pads; rim and fiducial keep-outs; antenna rule area notched around the module body.
- Pre-routed by script: 18 module escape vias, boost hot loop, the whole LED ring (5 V bus, data chain, cap stubs, feed), electrode and FDC vias, 7 stitching vias. LED ring order reversed to clockwise so the only data hop crosses the east gap. L1/C6 rotated, R32/R14/C12/C13 and three fiducials moved.
- Freerouting 2.2.4 tried and rejected: stalls at ~60 unrouted because the module's 0.6×0.4 mm pads have no legal exits. 127 connections left for hand routing.
- Board archived before routing at `hardware/archive/puck-carrier.kicad_pcb.2026-09-04-placed-unrouted`.

## 2026-09-04 (evening) — feature freeze

- Decided for spin 1: no UVC channel, no pH/ORP probes, no extra sensors; NFC stays a solder option. Rule: fewest things that can fail on the bench.
- Restored the bootloader pads TP21 BTN_DFU / TP22 BTN_FRESET (trimmed 09-01) as SMD pads; the east-rim column is now six pads.
- Added E5/E6 Ø3 mm gold aux pads on the sensor face on AIN4/AIN5 for the iridium-oxide pH-change experiment; pH demo otherwise = indicator patch in firmware.
- Board 120 footprints, DRC 0 violations, ERC 0 errors, parity clean.

## 2026-09-04 (later) — NFC kept off-board, expansion pads

- NFC: no PCB spiral fits; L2 became two SMD wire pads on the bottom (off-board ferrite flex/wound coil), C12/C13 beside them. Piezo pads renamed to the generic `WirePad` style.
- Four expansion pads TP23–TP26 (P0.28/AIN4, P0.29/AIN5, P0.00, P0.01) on the bottom east rim; `variant.h` gained `PIN_EXP_*`.
- AS7341 on the 3.3 V I2C bus confirmed OK from the datasheet (digital pins to 3.6 V).
- Routing deferred while Paolo adds features.

## 2026-09-04 — cleanup, correctness fixes, re-placement

- Repo: deleted 34 manual KiCad snapshots + `delete/` copy (safety tarball at `~/Projects/sensei-cup-backups-2026-09-04.tar.gz`), moved reviews to `docs/history/`, `assets/` → `docs/assets/`, added `docs/decisions.md` + this file, split STATUS.md down to a snapshot, first git commit.
- Docs: CLAUDE/README/WORKSPACE/spec/firmware/shopping-list corrected to the MDBT50Q, 4-layer, both-faces-assembled, 12-LED, dock-pad, epoxy-dip design.
- Schematic: UVC_EN/UVC_PD labels → no-connects on P0.11/P0.31; PZ1 footprint → `puck:PZ_WirePad_1x02_SMD` (new, 2 pads). ERC still 0 errors.
- Project: min clearance 0.15 mm; `power` net class assigned by pattern.
- Board: 51 footprint lib-ids relinked to qualified names; PZ1 footprint swapped; fiducials added (3 per face); U1 pulled inboard, all-layer antenna rule area drawn to spec; full re-placement to the radial scheme in `hardware/placement-guide.md`; refdes silk hidden, deliberate silkscreen added.

## 2026-08-31 — Design review

**Done (2026-08-31)** — 5 critical / 15 major confirmed, all fixed; review record in `docs/design-review.md`

## 2026-08-31 — Hardware

**Fix batch applied**: schematic (**103 symbols**, placement-only) now has MDBT50Q-1MV2 (U1), TPS61023 boost (U2, L1→1 µH, FB 750k/100k→5.06 V, D5 DNP), XC6206P182MR 1.8 V LDO for AS7341 (U10), EC bias network (R20–R23 + C16) + 4.7 µF coupling, all FETs AO3400A (Q1–Q5, piezo now FET-switched), LSM6DSO (U8, 0x6A), IM69D130 (U9), TP18 VBUS. **Review follow-up (2026-08-31, free-copper batch)**: 4-wire EC (E3/E4 force pads; E1/E2 sense on P0.04/P0.05 = AIN2/3, R26/R27 sense-node bias legs; 2-electrode stays the firmware fallback), FDC2 second CIN2 pad, DNP-v2 UVC channel (D7 275 nm + PD1 GUVC-T21GH + R25; UVC_EN=P0.11, UVC_PD=P0.31/AIN7), **EC drive moved P0.28/P0.29 → P0.22/P0.23** (old pads are ≤10 kHz low-freq; P0.28/P0.29 = AIN4/5 back to spares). All pins datasheet-verified (mdbt50q §2.5/§2.6). **Schematic WIRED (2026-08-31, incl. same-day USB-C-removal/dock delta)**: 108 symbols — R28 100k Q5-gate pull-down added per wiring guide; USB-C J2 + R18/R19 REMOVED; dock constellation CP1–CP4 (PAD_GND/PAD_DM/PAD_DP/PAD_5V on new footprint `puck:CHG_Pad_D2.0mm`, Ø2.0 mm, electrode-style), R29/R30 27 Ω series, U11 USBLC6-2SC6 ESD (flattened into `puck-extra` lib, SOT-23-6), TP19/TP20 UART, U7 STAT→`CHG_STAT`→P0.07. 237 wires / 234 labels / 33 no-connects, every pin wired or NC'd. FDC1004 SHLD1/SHLD2 pin type corrected Input→Output in `puck-extra` lib + schematic embed (they're the chip's guard drivers — clears the ERC undriven error). **ERC: 0 errors, 2 accepted warnings** (SHLD1 single-pin guard-net label, connects at layout pour; U8 SDO/SA0 GND-strap vs PWR_FLAG). PWR_FLAGs on 3V3/GND/VBUS + PAD_5V (VBAT flag dropped — U7 pin 3 is a Power output, flag there is a hard ERC conflict). Netlist machine-verified vs spec pin map (incl. P0.07=CHG_STAT) + wiring-guide edge list (diff empty) — **awaiting independent net review**, then Update PCB from Schematic. **Block 10b added (2026-08-31, status LED + glow ring)**: 125 symbols — D8+R31 1 k status LED on P0.12 (`LED_STAT`), D9 SOD-123 Schottky 5V→`5V_RING`, 6× XL-1010RGBC-WS2812B ring (D10–D15) on P1.00 (`RING_DATA`) via R32 220 Ω, chain nets RING_D0–D5, D15 DOUT NC'd, C18–C23 100 nF ring decouplers, #FLG05 PWR_FLAG on `5V_RING` (LED VDD pins are power_in). **P1.00 VERIFIED** in `docs/datasheets/mdbt50q-1mv2.pdf` §2.5: pin 47 castellation, "(recommended usage: QSPI)" only, NO low-frequency restriction → 800 kHz ring data OK, no pin substitution. New project footprint `puck:LED_XL-1010RGBC` from the XINGLIGHT datasheet drawing (`docs/datasheets/xl-1010rgbc.pdf`, fetched+verified); **XL-1010 pin numbering differs from stock `LED:WS2812B`** (1=DOUT 2=VDD 3=GND 4=DIN vs 1=VDD 2=DOUT) so a corrected `puck-extra:XL-1010RGBC` symbol is used — stock symbol would have cross-wired pads. 276 wires / 273 labels / 32 no-connects; netlist re-diffed empty; **ERC: 0 errors, 2 accepted warnings** (same SHLD1 + U8/#FLG02 pair, nothing new). **H1–H3 M2 holes REMOVED (2026-08-31, Paolo)** — 122 symbols; shell must retain the board instead (ledge + preload, see spec parts list); the stale H1–H3 footprints in the .kicad_pcb sit outside the new Ø40 outline and drop at Update-PCB-from-Schematic. Wiring pipeline archived in `scripts/wiring/` (regen proven byte-identical modulo uuids). **TP21/TP22 added (2026-08-31)** — commissioning item 2's promised DFU-force pads: `BTN_DFU`=P1.08 (§2.5 pin 25) / `BTN_FRESET`=P1.09 (pin 26), both datasheet-verified exposed/unrestricted; bootloader button pick now settled, spec pin map + spares updated; **124 symbols**, netlist diff empty, ERC still 0/2. `variant.h` updated: LED comment corrected (P0.12 is real D8 status LED now) + `PIN_BTN_DFU`(40)/`PIN_BTN_FRESET`(41); `pio run -e mdbt50q_puck` SUCCESS. **TP trim deferred to layout** (Paolo's open call: TP1, TP2/3, TP4/5, TP12 are the redundant candidates if the bottom face gets tight). Render: `renders/schematic-wired.png`

## 2026-09-01 — Trim (2026-09-01)

Test points cut 22 → 7 (kept 5 SWD TP13-17 + EC_A/EC_B TP6/TP7); UVC channel (D7/PD1/R25) fully removed from BOTH schematic and board — sch/pcb synced, ERC 0 errors, DRC placement 0. Schematic 124 → 106 symbols; board 118 → 105 footprints. Reliability passives (gate pulldowns, per-IC decouplers, ring caps) KEPT deliberately.

## 2026-09-01 — Condense + re-place (2026-09-01)

**Bottom was over-full (J1 couldn't fit clear of top electrode copper).** Decisions (Paolo): (1) **all 0603 passives → 0402, SOT-23-HS → nominal SOT-23** — 51 footprints swapped in BOTH sch + pcb, nets preserved, ~138 mm² reclaimed; (2) **JLC assembles BOTH sides** (bottom already has U8 LGA-14 + U4 0.5 mm VSSOP → not truly hand-solderable; reflow both sides unlocks 0402); (3) part-count trims (delete DNP D5, 2 resistor arrays, trim TP6/7) approved but **DEFERRED — space now ample, revisit if still needed**. **Re-placed net-aware** (`scratchpad/place/place_v2.py`): IC islands w/ decouplers hugging them, boost+LDO KEPT on bottom (top face fully committed to sensors + reserved ring rim — L1 won't fit up top), EC/FET/charger/dock zoned. **J1/U6/PZ1 (all through-hole) placed with pin-level top-copper keep-out** (U6 is TO-92 — was shorting to E1); U9 acoustic-port NPTH protected both faces. **0 courtyard overlaps both faces; DRC: 0 real errors** (17 remaining = intra-footprint fine-pitch pads on U8/U2 vs 0.2 mm rule → set min-clearance 0.15 mm in board setup; rest cosmetic silk). Ring D10–D21 + C18–C23 still parked for top-rim placement. ERC still 0/8. Backups: `*.pre-shrink0402`, `*.pre-v2`.

## 2026-08-31 — Placement

**DONE 2026-08-31 — Ø46 board, ALL parts placed, DRC placement-classes = 0.** Radial gold electrode spokes E1-E4 (east), center FDC1 pad, ring D10-D15 crescent, boost/optical/thermal zoned, module+dock+charger+battery+TPs bottom. Solved via simulated-annealing placer (scratchpad/place/anneal.py). **UVC v2 channel (D7/PD1/R25) CUT from this spin** — 10mm TO-5 photodiode didn't fit Ø46 cleanly; deferred to spin-2. Renders: renders/placement-final-{top,bottom}.png (SUPERSEDED by the 2026-09-01 condense pass above)
