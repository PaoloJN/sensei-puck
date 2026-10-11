# Placement Scheme — puck-carrier spin 1 (Ø46 mm, 4-layer)

The board is visible through clear resin, so placement IS the industrial
design. Everything is laid out on a polar system about the board centre.
Applied 2026-09-04 by `scripts/place_v3.py` (kept in the session scratchpad;
the numbers below are the source of truth). Board centre = (150, 100),
radius 23 mm. Angles are measured from east, counter-clockwise on screen
(north = 90°). `x = 150 + r·cos a`, `y = 100 − r·sin a`.

## Fixed axis

- **West = antenna.** U1 MDBT50Q-1MV2 on the bottom at (136.3, 100), rot −90,
  antenna end at the west rim, courtyard fully inside the outline. Board-level
  rule area `ANTENNA_KEEPOUT` (no tracks / vias / fills / footprints, all four
  copper layers): x 125.5–137.3, y 89.75–110.25, notched around the module
  body (x ≥ 127.9, y 94.2–105.8). The module footprint carries its own
  all-layer keep-out under the antenna itself. Nothing but silkscreen goes in
  the wedge on either face.
- **East = EC cell.** Four gold 2×8 mm pads, radial, centre radius 16.5 mm
  (span r 12.5–20.5), 16° pitch: E3 +24°, E1 +8°, E2 −8°, E4 −24°
  (force pair outside, sense pair inside).

## Top face (sensor face, points up in the water)

| Feature | Placement |
|---|---|
| Glow ring D10–D21 | r 20.5 mm, 21° pitch, two arcs, **clockwise order**: D10 at 142.5° → D15 at 37.5°, D16 at 322.5° → D21 at 217.5°. Rotation = angle + 90° (VDD and DOUT on the inner side, GND and DIN outer). Data hops LED-to-LED clockwise; the D15→D16 hop crosses the east gap at r 22.05 outside the electrode tips |
| Ring decouplers C18–C23 | r 18.6 mm at the pair midpoints 48°, 90°, 132°, 228°, 270°, 312°, tangential |
| FDC1 / FDC2 | **Concentric, on the axis at (148.4, 100)**: FDC1 = Ø7.9 disc (`puck:FDC_Sense_Pad_D7.9mm`), FDC2 = ring Ø9.2–12.0 (`puck:FDC_Sense_Ring_D10-12.8mm`, 46.6 mm², custom pad, no courtyard). Both mask-covered. 8.0 mm from the electrode inner ends |
| U9 mic + C11 | (142.2, 92.5) rot 90 / C11 (142.2, 89.0) — mirror of the pressure sensor |
| U5 pressure + C14 | (142.2, 107.5) / C14 (142.2, 111.0) — mirror of the mic |
| Aux electrodes E5/E6 | Ø3 mm gold pads (146.4, 91.0) and (146.4, 109.0), mirror pair beside the ring |
| Optical cluster | On the axis east of the ring: U3 (156.7, 100); D1 white (157.3, 93.5) and D2 850 nm (157.3, 106.5) mirrored; D3 365 nm (159.7, 100) rot 90 pointing at the electrodes. Silk W / IR / UV rotated to read with the antenna up |
| U6 DS18B20U+ (µSOP) | TOP face (151.6, 90.4) rot 90, the one off-axis part (no axis slot left) |
| Fiducials FID1–3, FID7 | Two mirror pairs: (154.5, 117) / (154.5, 83) and (147.6, 113.4) / (147.6, 86.6) |
| Silk | "WATER PUCK" + "spin 1 · 2026-09" in the west wedge, W / IR / UV by the LEDs, all rotated 90° so they read with the antenna at the top. All refdes hidden. **Eco1.User = dip mask**: outlines around everything that must stay free of epoxy (electrode fan, E5/E6, U5 port, U9 inlet) |

## Bottom face (base face)

Grid 0.1 mm, passives 0° / 90° only, rows at constant y.

| Block | Placement |
|---|---|
| Piezo (NW) | Q5 (134.6, 87.8); PZ1 two SMD wire pads (140.1, 86.5); R13/R24/R28 row y 82.7 at x 137.6/139.8/142.0 |
| Battery J1 (N) | THT pins (146, 82.5)/(148, 82.5), body toward the centre (bbox y 80.6–89.3). Pins sit between FDC2 and the north ring cap on the top face |
| SWD TPs (N) | TP13–TP17 row y 83.7, x 152.4 + 2.6·k; silk labels DIO/CLK/RST/VDD/GND above |
| Module support | C17 (146.4, 92.8), C3 (146.4, 97.0), rot 90 |
| NFC (N centre) | L2 off-board coil wire pads (153.4, 87.7) rot 90; tuning caps C12 (148.6, 90.5), C13 (153.4, 91.5); silk "NFC" |
| Centre column | U4 FDC1004 (150, 94.5) rot 90 behind the pads; C8 (153, 94.5); C16 (153, 97.6); U8 IMU (150, 101); C9 (153, 101); R14 OW pull-up (146.4, 90.5); R32 ring-data series (144.2, 90.8) next to the module escape vias |
| Boost (NE) | C5 (157.5, 86.6); U2 (157.5, 88.9); C6 (157.5, 91.2) **rot 180** (5 V pad toward U2); L1 (162.5, 89.1) **rot 180** (SW pad toward U2); R15/R16 y 93.5 at x 161/163.2; D9 (161.5, 95.9) |
| EC front end (E) | Row y 98.6: R20 R21 R22 R23 R26 R27 at x 155.5 + 2.2·k; C1 (157.5, 101.1), C2 (161.8, 101.1); row y 103.6: R1 R2 R3 R4; TP6 EC_A (164.9, 103.6), TP7 EC_B (165.2, 100.7) |
| East-rim pad column | Six 1.2×2.2 mm pads at x 168.8, y 99.3 + 2.0·k, rot 90, top to bottom: TP21 BTN_DFU, TP22 BTN_FRESET, TP23 EXP_A4 (P0.28), TP24 EXP_A5 (P0.29), TP25 EXP_00, TP26 EXP_01 |
| Charger (S centre) | Row y 105.6: R29 R30 R17 R31 at x 148.5 + 2.2·k; U11 (149.3, 108.7); U7 (154.3, 108.7); D6 (151.3, 112.5); D8 (156, 112.5); C10 (158.8, 112.5) |
| LDO + FETs (SW) | U10 (144.4, 111.7); C7 (147, 111.9); C15 (148.2, 111.9); Q1 (139.6, 107.8); Q2 (143.8, 107.8); Q3 (140.4, 111.7); row y 114.8: R8 R9 R10 R5 R6 R7 at x 138.3 + 2.2·k |
| Thermal (SE) | R11 2512 (163.4, 107.6); Q4 (161.5, 111.8); R12 (165.5, 112.2) |
| Dock | CP1–CP4 row y 118, x 143.25 + 4.5·k (GND / D− / D+ / 5V), silk labels below |
| Fiducials FID4–6 | (167, 92.5), (136.5, 112.3), (162, 115.5) |

## Rules kept

- Mic opposite the EC pads; IMU, optical and mic off the heater island.
- Through-hole pins (J1, U6) checked against every top-face courtyard and pad
  with ≥0.3 mm margin; the piezo uses SMD pads so it has no holes.
- Antenna wedge empty on both faces; NFC coil is off-board (wire pads), so no
  plane void is needed.
- DRC after placement: 0 clearance / courtyard / edge / keep-out errors;
  only unconnected-item errors remain (routing not started).

## Routing (started 2026-09-04 — hand routing from here)

**Stack:** 4 layers, F.Cu signal / In1 GND plane / In2 3V3 plane / B.Cu signal,
1.6 mm, ENIG. Planes are fill-only: do not route signals on In1/In2.

**Net classes (in the project file, DRC-enforced):**

| Class | Nets | Track | Clearance | Via |
|---|---|---|---|---|
| Default | everything else | 0.20 | 0.15 | 0.6 / 0.3 |
| power | GND, 3V3, VBAT, VBUS, PAD_5V, 1V8 | 0.40 | 0.15 | 0.8 / 0.4 |
| boost | 5V, BOOST_SW, 5V_RING | 0.50 | 0.15 | 0.8 / 0.4 |
| ec | EC_*, EC_NODE_D, EC_BIAS, EXP_A4/A5 | 0.25 | 0.20 | 0.6 / 0.3 |
| usb | PAD_DP/DM, USB_DP/DM | 0.20 (pair gap 0.15) | 0.15 | 0.6 / 0.3 |
| ring | RING_D0–D11, RING_DATA | 0.25 | 0.15 | 0.6 / 0.3 |
| led | LEDn_A/K, HTR_SW, PZ_DRV | 0.35 | 0.15 | 0.6 / 0.3 |

**Already on the board (by `scripts/route_prep.py` + `scripts/route_pre.py`):**
- Zones: GND on In1 (full) with one SHLD1 guard island r 6.9 under the disc + ring (priority 2);
  3V3 on In2 (full); GND fills top + bottom (thermal, 0.25 spokes).
- Rule areas: antenna wedge (all four Cu layers, notched around the module body
  so its pads stay reachable); electrode sector ±32° beyond r 10.5 — no fills or
  tracks on In1/In2, no fill on top; r 6.7 around the FDC pair — no In2 copper, no
  top fill; rim r > 22.35 — no tracks/vias (edge clearance); r 1.4 around fiducials.
- Module: 18 escape stubs + vias on every inner-row pad (0.6×0.4 mm pads at
  0.8 mm pitch have no sideways exit). Outer-row pads exit outward. The pads
  beside the antenna (SWDIO, SWCLK, EC_DRV_LO, BOOST_EN) exit south through the
  1.4 mm corridor at y 105–106.3; nothing else goes in that corridor.
- Boost: SW (U2→L1), VBAT (U2↔C5, L1↔C5), 5V (U2↔C6), R15–R16 tie.
- LED ring: 5V_RING bus at r 19.5 (0.5 mm) with the east-gap crossing at r 21.5;
  VDD stubs; cap stubs; data chain D10→D21 clockwise; RING_D0 from R32 under J1
  to D10; 5V_RING feed D9 → via (158.9, 95.9) → top.
- Electrodes E1–E4: stub + via each (EC_A (160.8, 94.9), EC_SENSE_A (162.0, 99.6),
  EC_SENSE_B (162.0, 102.55), EC_B (160.8, 105.1)). FDC: CIN1 via (150.5, 98.2) inside the
  disc, CIN2 via (146.3, 105.0) inside the ring + bottom run to U4, SHLD1 via (155.9, 97.0)
  with a bottom run around U4.
- 6 GND stitching vias; DRC 0 errors; 127 connections left.

**Suggested order for the rest:**
1. Power first: VBAT (J1 → U7 VBAT → U1 pin 30 → C5/U2), 5V (C6 → R15 → D9 anode,
   and C6 → R5/R6/R7 → R11 heater), every 3V3 pad gets a via to In2, GND pads
   not already on a fill get a via. BOOST_FB: U2 pin 1 to the R15/R16 tie.
2. EC front end on B.Cu only, short, away from 5V: electrode vias → R/C block,
   block → module escape vias (EC_A, EC_B, EC_SENSE_A/B, EC_DRV_LO/HI, EC_BIAS).
3. I2C SDA/SCL: U1 → U4, U8 (bottom) and U3, U5 (top, via). PDM_CLK/DATA → U9 (top).
4. SWD/DFU: SWDIO, SWCLK through the corridor to TP13/TP14; RESET → TP15;
   BTN_DFU/FRESET → TP21/TP22; UART pins stay unrouted.
5. Dock: PAD_5V → D6 → VBUS → U7/U1; USB_DP/DM as a pair through R29/R30 and U11
   to CP2/CP3; CHG_STAT.
6. Gates and loads: LED_WHITE/850/365, HEATER_EN, PIEZO → Q1–Q5; LEDn_A/K up to
   D1–D3; HTR_SW → R11; PZ_SW/PZ_DRV → PZ1 pads; LED_STAT → D8/R31; IMU_INT → U8.
7. OW_DQ → U6 (top) and R14; NFC1/NFC2 → C12/C13 → L2; EXP_00/01 → TP25/26;
   EXP_A4/A5 → E5/E6 and TP23/24.
8. Refill zones, DRC, then add more GND stitching vias wherever a 0.6 via fits.
