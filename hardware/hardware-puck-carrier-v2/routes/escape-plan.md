# v2 escape plan (2026-10-16)

Written before the signal routing, the way a layout engineer plans a dense part before the first trace.
Coordinates in board mm. Module U1 on B.Cu, body x 128–144.6, y 93.8–106.2. Antenna keepout (all layers)
x < 137.3 for y 89.75–93.6 and y 106.5–110.25, x < 127.9 in between. Rule area MODULE_RULES (B.Cu,
x 137.4–146.2, y 93.4–106.6): 0.1 mm trace / 0.1 mm clearance, EC nets 0.15, vias 0.5 / 0.2.

## Module pads and their exits

| Exit | Pads (net) | Route |
|---|---|---|
| North, direct | 8 BTN_FRESET, 10 EXP_A5, 12 EC_SENSE_A, 14 EC_BIAS_EN | straight north from the outer row |
| North, east of keepout | 4 PDM_DATA, 6 PDM_CLK | north to y ≈ 94.3, east to x > 137.3, then north |
| North channel (x 140.4–143.1 at y 95) | 9 EC_B, 11 EC_A, 13 EXP_A4 (inner north row); 21 EC_SENSE_B (inner column); 40 RESET (inner south row); 52 NFC1, 54 NFC2 | under the module body, out between pad 14 and pad 15; 7 nets, capacity 13 at 0.1 mm |
| East → south lane | 16 SCL, 17 EXP_00, 18 EXP_01, 20 CHG_STAT, 22 BTN_DFU, 24 LED_STAT, 26 SDA | east of the pads, south along x 144.6–145.6 (east of the 3V3 trunk at 144.3, west of C3 at 145.74), into the lane y 102.8–105.0 under U8 towards x 152+; destinations are all south-east |
| South, direct | 34 USB_DM, 35 USB_DP, 37 LED_WHITE, 39 LED_365, 41 HEATER_EN, 44 BOOST_EN, 46 EC_DRV_LO, 48 UART_TX, 51 SWDIO, 53 SWCLK | straight south from the outer row |
| South, through 1.6 mm outer gaps | 49 UART_RX (+50 LED_850) between pads 51/48; 47 RING_DATA + 45 EC_DRV_HI between 48/44; 43 IMU_INT + 42 PIEZO between 44/41 | two traces per gap at 0.1 mm |
| West, then north | 3 OW_DQ | north to y ≈ 94.3, east along y 94.3 past x 137.3, north |

Pads with no net after the swaps: 5, 7, 19, 23, 25, 27, 29, 31, 36, 38, 56–61.

## Lanes off the module

- **North band** y 88.75–89.95 between PZ1 pad 2 (y ≤ 88.5) and R32/R14/C12 (y ≥ 90.2): east-west bus for the north-channel nets heading east; the R14 3V3 via at (145.14, 89.75) must move south of R14.
- **C3 corridor** x 143.75–145.6, y 94–99.5: the east-column nets going south, and nothing else. GND via (144.5, 93.3) (U9's) moves west so the corridor can also exit north if needed.
- **South lane** y 102.8–105.0, x 144.6–152: east-column nets to U8 (I2C), R1/R2, U7, R31, U11, the east test points. Vias only east of x 154 (FDC no-via disc, r 6.45 around (148.4, 100)).
- **EC bundle**: EC_A, EC_B, EXP_A4 from the north channel east along the north band to x ≈ 155, then south-east into the EC front end (R20–R27 at y 98.6, C1/C2 at y 101.1, E1–E4 on F.Cu). EC_SENSE_A from pad 12 joins the same band. EC_SENSE_B from the inner column via the north channel.
- **USB pair** 34/35 south to R29/R30 (y 105.6) then to U11; dock pads CP2/CP3 at y 118 via U11 pads 1/6 and 3/4.

## Layer roles (decided 2026-10-16, evening)
- F.Cu: top-side pads and a stub to a via. No signal runs. Accepted exception: the DC rails VBAT, 5V and 1V8 at the rim, routed by hand before the rule, stay.
- GND (In1): solid plane, never routed.
- PWR (In2): second signal layer. The 3V3 pour fills around whatever is routed there. Keep out of KO_EC_PLANES (x > 158.9, y 88–112) and the antenna keepout.
- B.Cu: first choice for everything.
A through via connects to a layer only where a trace is drawn on that layer; to cross on PWR, drop a via, step the active layer to PWR, cross, via back.

## Working method
Planner/applier split: planners (people or agents) write spec JSON against a frozen snapshot and run the file checker; one applier re-checks against the live board and applies in sequence through `cl route --apply`, which gates with kicad-cli. Nothing is accepted that makes errors or unconnected counts grow.

## Rules
One via per net crossing, no autorouter on these nets, every spec goes through `cl route` and the gate,
length over 1.5× straight-line gets re-planned.

## Evening finding: the south-west four (2026-10-16)

HEATER_EN (pad 41), EC_DRV_LO (46), EC_DRV_HI (45) and BOOST_EN (44) have no clean exit as placed:

- Under the module there is a third pad column, 56–61 (x 136.55–137.15, y 97.8–102.2, no nets). Columns from pads 44/45 at x 137.4/137.7 fit, but a 0.5 mm via beside either column does not (0.15 mm EC clearance), and nothing passes north between the staggered north pad rows west of x 140.25.
- South of the module the PWR band is fenced: LED_850's row at y 104.95 (x 135.1–142.25) and its drop at x 142.25, LED_WHITE's L (x 140.6 down to y 107.55, west to the Q1.1 via at (137.6, 108.75)), the VBAT PWR diagonal to (144.65, 106.7), the GND vias at (138.7, 105.65) / (141.2, 106.5) and the antenna keepout (x < 137.3 for y 106.5–110.25). Q1.1 itself is reachable only from the west gap, which is why LED_WHITE sits where it does.
- East side is ready: with the SCL PWR column cut back to y 97.2, four PWR rows at y 99.65–101.05 can cross under the FDC to vias at (157.85, 102.4) → R3.1, (158.6, 102.35) → R4.2, a column at x 157.6/158.1 up to (157.0, 92.5) → R33.1, and x 151.6 down to y 113.3 → (159.85, 113.95) → Q4.1. Draft: `sw-bundle-draft.json`.

Options, cheapest first:
1. **Move the LED drivers.** Shift Q1/Q2/Q3 (and R8/R9/R10 next to their gates) ~2 mm south-east so a PWR band y 105.2–107.4 and a B.Cu gap east of Q1.1 open up; LED_WHITE/LED_850/LED_365 are then re-routed from scratch (cheap, scripted).
2. **Pin pass 4.** Give the four nets pads whose exits are free. Candidates: the east inner column 19/23/25 (P0.26/P0.07/P1.08) with the lane re-spaced to 0.2 mm pitch (six rows fit between the SCL row and VBUS), which covers two or three of them; BOOST_EN can also take a north-row pad and ride the north band to R33.
3. Accept one short F.Cu crossing south of the module (breaks the layer rule; the top face there carries U5).

## 2026-10-17: what is routed, what is planned, what is handed over

Done in file mode (0 errors, 61 open): Q1 rotated, D1/D3 moved under D2, R5–R7 on the top face by their LEDs, pin pass 4 (pads 37 LED_850, 39 LED_WHITE, 41 HEATER_EN, 48 LED_365, 50 UART_TX), old south-west copper removed, LED gates routed (`gates.json`), CHG_STAT on a top-side column from the lane via, VBAT U7.3→C25 bottom link at y 111.5, nine GND stub vias dropped (pads use the bottom pour).

Planned, checked on paper only — coordinates to route or to feed the interactive router:

- **VBAT to the module** (PWR): from the via (142.4,103.05) north along x 142.4 to y 91.6, east along y 91.25 to x 153.25, north at x 153.6 to y 90.0, east along y 89.75, into the via (155.5,89.15). Remove the dangling stub (142.4,103.05)-(142.4,104.0).
- **Four-net band** south of the module (PWR), rows north→south BOOST_EN 105.45, EC_DRV_HI 105.9, EC_DRV_LO 106.4, HEATER_EN 106.75. Vias just below the pads: BOOST (137.7,105.3), HI (137.25,105.85), LO (136.7,105.4), HEATER (139.25,106.85). East ends: BOOST turns north at x 151.9, row y 98.15 east to 157.6, channel x 158.1 up to y 93.6, via (157.0,92.5) → R33.1 (already linked to U2.2). HI turns north at x 152.25, row y 100.0, diagonal to a via at (158.6,102.35), bottom side y 102.95 into R4.2. LO turns north at x 152.6, row y 102.1, via (157.85,102.4), bottom side into R3.1. HEATER goes east to x 155.3, down to y 113.3, east, via (159.55,114.25) below Q4.1 (Q4.1→R12.1 is routed). Antenna keepout corner (137.3,106.5): nothing west of 137.3 below y 106.5.
- **LED cathodes**: /LED1_K from Q1.3 (via ~(138.3,108.6)), /LED3_K from Q3.3 (via (141.2,112.65)) on PWR lanes y 109.35 / 109.65 east to the pocket below U7, then vias up to the top face; /LED2_K from Q2.3 (via (144.5,108.6)) on the top face along y 110.75, up between D1 and D3 into D2.1. The pocket under U7 (x 152.5–155, y 110–111.8) is where this keeps colliding with CHG_STAT, the VBAT link and D8; push-and-shove in KiCad is the better tool there.
- **Anodes + 5V**: R6.2→D2.2 and R5.2→D1.2 are 1 mm top stubs; R7.2→D3.2 likewise; 5V: via on the 5V bottom track at (160.49,94.6), top-side column x 160.5 down to R6.1 and R5.1 (E4's left edge is 161.01); R7.1 to the 5V top rail. Consider shifting the 5V top rail from y 113.25 to 113.6 if D3 needs the room.
- Still untouched: north channel bundle, north direct pads, SWDIO/SWCLK, TP21–24 (relocate or delete), /PAD_DP, /EC_NODE_D, /PZ_DRV, /PAD_5V, 1V8→U3.1, /RING_D0.
