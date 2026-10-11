# Changelog

Dated work log, newest first. Moved out of STATUS.md on 2026-09-04; the
2026-08-31 / 09-01 entries are the original STATUS table cells, verbatim.

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
