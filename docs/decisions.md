# Decisions (one line each, newest first)

Dated calls that are not derivable from the files. Add a line when something is
settled; do not rewrite history — supersede with a new line.

| Date | Decision | Why |
|---|---|---|
| 2026-09-04 | Piezo PZ1 gets two SMD wire pads (`puck:PZ_WirePad_1x02_SMD`), not a THT test point | The old single-pad footprint dropped pin 2; SMD keeps holes off the sensor face |
| 2026-09-04 | Reference-designator silkscreen hidden on both faces; only deliberate marks (name, dock/SWD labels, pin-1 dots) | JLC assembles from the CPL; the board is visible through clear resin |
| 2026-09-04 | Power net class assigned by pattern (GND, 3V3, VBAT, 5V, VBUS, 5V_RING, PAD_5V); board min clearance 0.15 mm | Fine-pitch LGA/SOT-563 pads need 0.15; power nets get 0.4 mm tracks |
| 2026-09-04 | Repo history lives in git; manual `.pre-*` snapshots deleted and gitignored; three milestone snapshots kept in `hardware/archive/` | 34 snapshot files were drowning the project directory |
| 2026-09-04 | NFC kept, coil goes OFF-BOARD: L2 = ferrite-backed flex / wound 13.56 MHz antenna on two SMD wire pads (bottom, `puck:WirePad_1x02_SMD_1.5x3mm`), C12/C13 beside them, retune after assembly | No PCB spiral fits at Ø46 without a 14 mm void in all planes; Paolo wants NFC in |
| 2026-09-04 | Routing deferred until Paolo finishes adding/editing features | His call; placement is stable, the placer script re-runs in seconds |
| 2026-09-05 | Sensor face re-laid symmetric about the antenna→electrode axis: FDC pads concentric (disc + ring) on the axis, mic/pressure mirror pair, optical cluster on the axis, aux pads mirrored, fiducials paired; U6 becomes DS18B20U+ (µSOP-8) on the top face | Paolo: the face is what people see through the resin; the TO-92 was the ugliest part and its pins kept colliding with sensor copper |
| 2026-09-05 | What touches water (masked before the dip): E1–E4, E5/E6, U5 gel port, U9 inlet, dock pads. Everything else under clear epoxy, FDC discs included | Drawn on Eco1.User as the dip-mask layer |
| 2026-09-04 | Routing: no autorouter. Planes, guards, module escapes and the LED ring are scripted; Paolo hand-routes the remaining 127 connections | Freerouting stalled at ~60 unrouted on the 0.6×0.4 mm module pads; hand routing is faster than cleaning its output |
| 2026-09-04 | LED ring wiring: 5 V bus inside the LEDs at r 19.5, data chain clockwise, both cross the east gap outside the electrode tips (bus r 21.5, data r 22.05); nothing crosses the antenna wedge | The west hop collided with the module escape vias; the east gap has room outside the tips |
| 2026-09-04 | Feature freeze for spin 1, rule = fewest things that can fail on the bench: NO UVC channel, NO pH/ORP probes (a wire defeats the puck), NO extra sensors. NFC stays a solder option | Paolo: "I gotta be able to make this and it working" |
| 2026-09-04 | Bootloader pads TP21 (BTN_DFU, P1.08) / TP22 (BTN_FRESET, P1.09) restored as SMD pads in the east-rim column | They were trimmed on 09-01 but the commissioning plan needs tweezer-to-GND DFU entry before the dip |
| 2026-09-04 | Two Ø3 mm gold aux pads E5/E6 on the sensor face, differential on AIN4/AIN5 (same nets as EXP_A4/EXP_A5) | Free option for a planar iridium-oxide pH-change electrode (E5) with a bare-gold pseudo-reference (E6); unused they are two gold dots |
| 2026-09-04 | pH for the demo = indicator-patch mode (firmware only, AS7341 reads a colour disc over the optical cluster) | Already in the spec; no hardware |
| 2026-09-04 | Four expansion pads (TP23–TP26) bring out P0.28/AIN4, P0.29/AIN5, P0.00, P0.01 on the bottom east rim | Only way to try a surprise sensor or the v2 pH probe without a spin 2; costs no BOM line |
| 2026-09-04 | No I2C level shifter for the 1.8 V AS7341 on the 3.3 V bus | AS7341 datasheet: digital pins abs-max 3.6 V, VIH min 1.26 V, open-drain outputs — 3.3 V pull-ups are within spec |
| 2026-09-01 | UVC channel (D7/PD1/R25) cut from spin 1; P0.11 / P0.31 no-connect, reserved for v2 | 10 mm TO-5 photodiode did not fit Ø46 cleanly |
| 2026-09-01 | JLC assembles BOTH faces; all discrete passives 0402; SOT-23 nominal | Bottom already carried LGA-14 + 0.5 mm VSSOP (not hand-solderable); 0402 freed ~138 mm² |
| 2026-09-01 | 12-LED ring (D10–D21) instead of 6 | Even rim spacing at Ø46 |
| 2026-09-01 | Test points trimmed 22 → 7 (SWD ×5 + EC_A/EC_B) | Bottom face was over-full |
| 2026-08-31 | Boost (U2/L1) and 1.8 V LDO (U10) stay on the bottom | Top face is committed to sensors + ring rim |
| 2026-08-31 | Board Ø46 mm, 4 layers (Sig/GND/PWR/Sig), ENIG, black mask | Ø40 too cramped; solid GND under EC ADC, mic, boost loop |
| 2026-08-31 | M2 mounting holes removed; shell/pot retains the board | Area and inner-layer routing freedom |
| 2026-08-31 | USB-C removed; 4-pad magnetic dock (GND/D−/D+/5V) carries charge + native USB | Zero external connectors on a potted device |
| 2026-08-31 | Clear epoxy dip after commissioning gates (supersedes serviceable O-ring shell) | Simplest waterproofing for a POC; board stays visible; DFU OTA is the reflash path |
| 2026-08-31 | 4-wire EC cell (E3/E4 force, E1/E2 sense on AIN2/AIN3); EC drive on P0.22/P0.23 | Fouling-immune sense pair; old drive pins were ≤10 kHz pads |
| 2026-08-31 | Bootloader buttons: BTN_DFU = P1.08 (TP21), BTN_FRESET = P1.09 (TP22) | Datasheet-verified unrestricted pins |
| 2026-08-31 | Design-review part swaps: MT3608 → TPS61023, LIS2DW12 → LSM6DSO, MP34DT06J → IM69D130; XC6206 1.8 V LDO for AS7341 | See `docs/history/design-review.md` |
| 2026-08-30 | Brain: Raytac MDBT50Q-1MV2 bare module replaces the XIAO carrier (and the E73 interim) | Best-documented nRF52840 module; XIAO stays the bench mule |

## 2026-10-16 — Module pin swap and 0.1 mm local rules instead of more autorouting

The MDBT50Q east and inner pad columns cannot be escaped at 0.15 mm rules (0.4 mm gaps, inner rows cannot pass the outer rows). Decision: write the escape plan first, then let the pin assignment follow it: EC_SENSE_A, PDM_DATA, PDM_CLK and BTN_FRESET to spare outer north pads (P0.31, P1.11, P1.13, P1.15); CHG_STAT, BTN_DFU, LED_STAT and SDA to the freed east-column pads (P0.04, P0.06, P0.08, P1.09) because their destinations are south-east and the east column feeds the south lane; LED_850 and OW_DQ to spare pads that exit directly (P1.02, P1.10). The module's north channel then carries 7 nets instead of 13 and add a 0.1 mm trace/clearance rule area under the module with 0.5/0.2 vias, which JLCPCB's 4-layer process (0.09 mm) supports. Firmware pin defines follow the spec table. Alternatives rejected: whole-board autorouting (tried five ways in October, boxes the module in) and a second module placement (new spin).
