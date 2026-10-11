# Placement Scheme — puck-carrier spin 1 (Ø46 mm, 4-layer)

The board is visible through clear resin, so placement IS the industrial
design. Everything is laid out on a polar system about the board centre.
Original placement was generated in September. October corrections below
supersede that generator. The saved PCB is the coordinate source of truth;
do not rerun placement scripts on a routed board. Board centre = (150, 100),
radius 23 mm. Angles are measured from east, counter-clockwise on screen
(north = 90°). `x = 150 + r·cos a`, `y = 100 − r·sin a`.

## Fixed axis

- **West = antenna.** U1 MDBT50Q-1MV2 on the bottom at (136.3, 100), rot −90,
  antenna end at the west rim, courtyard fully inside the outline. Board-level
  rule area `ANTENNA_KEEPOUT` (no tracks / vias / fills / footprints, all four
  copper layers): x 125.5–137.3, y 89.75–110.25, notched around the module
  body (x ≥ 127.9, y 93.6–106.5). The module footprint carries its own
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
| U5 pressure + C10 | (142.2, 107.5) / C10 (142.2, 111.0) — mirror of the mic |
| Aux electrodes E5/E6 | Ø3 mm gold pads (146.4, 91.0) and (146.4, 109.0), mirror pair beside the ring |
| Optical cluster | On the axis east of the ring: U3 (156.7, 100); D1 white (157.3, 93.5) and D2 850 nm (157.3, 106.5) mirrored; D3 365 nm (159.7, 100) rot 90 pointing at the electrodes. Silk W / IR / UV rotated to read with the antenna up |
| U6 DS18B20U+ (µSOP) | TOP face (151.6, 90.4) rot 90, the one off-axis part (no axis slot left) |
| Fiducials FID1–3, FID7 | Two mirror pairs: (154.5, 117) / (154.5, 83) and (147.6, 113.4) / (147.6, 86.6) |
| Silk | "WATER PUCK" + "spin 1 · 2026-10" in the west wedge, W / IR / UV by the LEDs, all rotated 90° so they read with the antenna at the top. All refdes hidden. **Eco1.User = dip mask**: outlines around everything that must stay free of epoxy (electrode fan, E5/E6, U5 port, U9 inlet) |

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
| Charger (S centre) | Row y 105.6: R29 R30 R17 R31 at x 148.5 + 2.2·k; U11 (149.3, 108.7); U7 (154.3, 108.7); D6 (151.3, 112.5); D8 (156, 112.5); C24 (156.3, 115.1), C25 (157.6, 109.4), both 10 µF / 16 V 1206 |
| LDO + FETs (SW) | U10 (144.4, 111.7); C7 (147, 111.9); C15 (148.2, 111.9); Q1 (139.6, 107.8); Q2 (143.8, 107.8); Q3 (140.4, 111.7); row y 114.8: R8 R9 R10 R5 R6 R7 at x 138.3 + 2.2·k |
| Thermal (SE) | R11 2512 (163.4, 107.6); Q4 (161.5, 111.8); R12 (165.5, 112.2) |
| Dock | Row y 118; top-coordinate x 146.19 / 148.73 / 151.27 / 153.81: CP1 GND / CP3 D+ / CP2 D− / CP4 +5V. 2.54 mm pitch; bottom view mirrors the row |
| Fiducials FID4–6 | (167, 92.5), (136.5, 112.3), (162, 115.5) |

## Rules kept

- Mic opposite the EC pads; IMU, optical and mic off the heater island.
- Through-hole pins (J1) checked against every top-face courtyard and pad
  with ≥0.3 mm margin; the piezo uses SMD pads so it has no holes.
- Antenna wedge empty on both faces; NFC coil is off-board (wire pads), so no
  plane void is needed.
- DRC after placement: 0 clearance / courtyard / edge / keep-out errors;
  see the latest check report; earlier placement-only results are not release evidence.

## Routing and review

The original stack is F.Cu signal / In1 GND + SHLD1 / In2 3V3 / B.Cu signal.
Routing experiments may use In2 for signals outside sensing keep-outs, but any
candidate must be checked against the original board rules and copper pours.
Do not copy a router session directly into a fabrication release.

R33 (BOOST_EN pulldown) is on B.Cu at (157.5, 93.5). C14 is on F.Cu at
(144.3, 114.0), adjacent to the LDO area. C10 is the pressure bypass on F.Cu.
SHLD1's stitch is at (154.5, 97.0), inside its guard pour; the older (155.9,97)
position did not reach the plane. Keep CIN traces short and isolated from switching.

Critical manual review: boost current loop/return, charger bypass return, USB pair
routing and ESD placement, EC sense paths, FDC shield connection, ring current
return and antenna clearance with the actual battery and enclosure.

Run `python3 hardware/hardware-puck-carrier/scripts/verify_design.py` from the
repository root. A nonzero exit means the CAD release gate is not passed. The
script produces netlist, BOM, ERC/DRC and source hashes in the project's `checks/`.
See `../docs/validation-plan.md` for mechanical and physical gates.
