# Library setup — puck-carrier (integrated spin 1)

KiCad installed: **10.0.3** (`/Applications/KiCad/KiCad.app`). Everything below was verified against the
installed stock libraries; project-local parts live under `lib/` and are registered in the
project `sym-lib-table` / `fp-lib-table` with `${KIPRJMOD}` paths, so the project is portable
to any machine with no global-config changes.

Design basis: **integrated board spec** (`../carrier-board-spec.md`) — bare MDBT50Q-1MV2 nRF52840
module, on-board sensors, LiPo + MCP73831 + USB-C, TPS61023 5 V boost. Updated 2026-08-31 for the
design-review fix batch (`../../docs/design-review.md`): TPS61023, LSM6DSO, IM69D130, XC6206P182MR,
all FETs AO3400A, EC bias network + 4.7 µF coupling, TP18. Updated again 2026-08-31
(review follow-up, free-copper batch): E3/E4 force electrodes (4-wire EC), FDC2 second
sense pad, DNP v2 UVC channel (D7/PD1/R25), EC drive pins moved to P0.22/P0.23. The
earlier XIAO-carrier identifiers are kept at the bottom (superseded, still in the libs —
the XIAO stays the bench mule).

```
hardware-puck-carrier/
├── sym-lib-table                  # puck -> Seeed XIAO lib; puck-extra -> puck-extra.kicad_sym
├── fp-lib-table                   # puck -> lib/footprints/puck-parts.pretty
└── lib/
    ├── symbols/
    │   ├── Seeed_Studio_XIAO_Series.kicad_sym        # Seeed OPL (XIAO = bench mule, off-board)
    │   └── puck-extra.kicad_sym                      # MDBT50Q-1MV2 (U1), TPS61023 (U2, authored), LSM6DSO (U8, authored), FDC1004, MS5837; retired-but-kept: E73, LIS2DW12, generic PDM mic
    ├── footprints/puck-parts.pretty/
    │   ├── MDBT50Q-1MV2.kicad_mod                    # new U1 — copied from KiCad 10.0.3 stock RF_Module:Raytac_MDBT50Q
    │   ├── E73-2G4M08S1C.kicad_mod                   # RETIRED (kept) — was joric/nrfmicro import
    │   ├── SOP50P490X110-10N.kicad_mod               # FDC1004 VSSOP-10 (SnapEDA)
    │   ├── XDCR_MS583702BA01-50.kicad_mod            # MS5837 LGA (SnapEDA)
    │   ├── EC_Electrode_2x8mm.kicad_mod              # custom, mask-open gold pad
    │   ├── FDC_Sense_Pad_10mm.kicad_mod              # custom, mask-covered copper pad
    │   └── XIAO-nRF52840-{SMD,DIP}.kicad_mod         # superseded (bench mule)
    └── 3dmodels/                                     # see 3D models section
```

## Parts table — integrated spin 1 (spec → exact identifiers)

| Ref | Part | Symbol (library:name) | Footprint (library:name) | Status / notes |
|---|---|---|---|---|
| U1 | **Raytac MDBT50Q-1MV2** (nRF52840, chip antenna) | `puck-extra:MDBT50Q-1MV2` (copied from KiCad 10.0.3 stock `RF_Module:MDBT50Q-1MV2`; all 61 pins re-verified 1:1 against Raytac datasheet §2.5 pin table) | `puck:MDBT50Q-1MV2` (copied from stock `RF_Module:Raytac_MDBT50Q`, KLC-reviewed; **all 61 pad centers verified 0-mismatch** against datasheet §2.2 land pattern — see MDBT50Q verification notes) | Module 10.5×15.5×2.05 mm; pads 0.6×0.4 mm; bottom/mid-row pitch 0.8 mm, side rows staggered 0.8 mm; antenna keep-out zones built into the footprint (match datasheet §2.2/2.3). 3D: `lib/3dmodels/MDBT50Q-1MV2.step` |
| *(U1 old)* | *E73-2G4M08S1C — RETIRED, kept in libs* | `puck-extra:E73-2G4M08S1C` (authored, 43 pins verified against EBYTE user manual pin table) | `puck:E73-2G4M08S1C` (imported from [joric/nrfmicro](https://github.com/joric/nrfmicro), proven fabricated) | Superseded by MDBT50Q-1MV2 (2026-08-30); files stay for reference. Old caveat (inner-row pad offset ~0.6 mm between community footprints) no longer relevant |
| U2 | **TPS61023 boost** (was MT3608 — review M4: true load disconnect) | `puck-extra:TPS61023` (**authored** minimal 6-pin symbol; pin table verified vs TI datasheet SLVSF14B Fig. 5-1: 1 FB, 2 EN, 3 VIN, 4 GND, 5 SW, 6 VOUT) | `Package_TO_SOT_SMD:SOT-563` (stock — TPS61023DRLR = DRL = SOT-563) | Datasheet on file `../../docs/datasheets/tps61023.pdf`. FB math below. L1 must be 0.37–2.9 µH (→ 1 µH) |
| U3 | AS7341 | `Sensor_Optical:AS7341DLG` (stock — note the `DLG` suffix) | `Package_LGA:AMS_OLGA-8_2x3.1mm_P0.8mm` | stock, resolves |
| U4 | FDC1004DGSR | `puck-extra:FDC1004DGSR` (SnapEDA import, upgraded to v10 format) | `puck:SOP50P490X110-10N` (SnapEDA) | 3D: `lib/3dmodels/FDC1004DGSR.step` |
| U5 | MS5837-02BA | `puck-extra:MS583702BA01-50` (SnapEDA import) | `puck:XDCR_MS583702BA01-50` (SnapEDA) | 3D: `lib/3dmodels/MS5837-02BA.step`; hand-place, gel port |
| U6 | DS18B20+ TO-92 | `Sensor_Temperature:DS18B20` (stock, derived from MAX31820; pins 1=GND 2=DQ 3=VDD) | `Package_TO_SOT_THT:TO-92_Inline` | stock, resolves |
| U7 | MCP73831-2 charger | `Battery_Management:MCP73831-2-OT` (stock) | `Package_TO_SOT_SMD:SOT-23-5` | stock, resolves |
| U8 | **LSM6DSO IMU** (was LIS2DW12 — review swap) | `puck-extra:LSM6DSO` (**authored**: byte-copy of stock `Sensor_Motion:LSM6DSM`, renamed — all 14 pins verified identical to LSM6DSO datasheet DS12140 Table 1; addr 0x6A with SDO/SA0→GND, D4h/D5h confirmed §5.1.1) | `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` (stock; LSM6DSO is LGA-14 2.5×3 mm P0.5) | Datasheet on file `../../docs/datasheets/lsm6dso.pdf`. Old `puck-extra:LIS2DW12` kept, retired |
| U9 | **IM69D130 PDM mic** (was MP34DT06-class placeholder — review swap) | `Sensor_Audio:IM69D130` (stock!) | `Sensor_Audio:Infineon_PG-LLGA-5-1` (stock, StepUp-generated from Infineon's PG-LLGA-5-1 package page — IM69D130's package, 4×3×1.2 mm) | Pin table verified vs Infineon datasheet Table 7 (1 DATA, 2 VDD, 3 CLOCK, 4 SELECT, 5 GND); PDM clock 0.4–3.3 MHz. Datasheet on file `../../docs/datasheets/im69d130.pdf`. Placeholder RESOLVED; old `puck-extra:PDM_Microphone` kept, retired |
| U10 | **XC6206P182MR 1.8 V LDO** (AS7341 VDD only — review C1) | `Regulator_Linear:XC6206PxxxMR` (stock; Value carries the P182 1.8 V variant; pins GND=1/VO=2/VI=3 match XC6206 SOT-23) | `Package_TO_SOT_SMD:SOT-23_Handsoldering` | stock, resolves; ~1 µA Iq; C14/C15 1 µF in/out |
| J1 | LiPo JST-PH 2-pin | `Connector_Generic:Conn_01x02` | `Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal` | stock; battery = protected pouch cell on this connector |
| *(J2 old)* | *USB-C 16P — REMOVED 2026-08-31, replaced by the CP1–CP4 dock pads* | — | `puck:USB_C_Receptacle_HRO_TYPE-C-31-M-12` kept in the lib | retired |
| PZ1 | Piezo disc wire pads | `Device:Buzzer` | `puck:PZ_WirePad_1x02_SMD` (2 × 2×4 mm SMD pads, 2026-09-04 — replaces the 1-pad THT test point that dropped pin 2) | project-local |
| D1–D3 | SMD LEDs 3528 white/850/365 | `Device:LED` | `LED_SMD:LED_Everlight-SMD3528_3.5x2.8mm_67-21ST` (closest stock 3528) | **PLACEHOLDER-ish** — exact LCSC LEDs at BOM time (verify true 365 nm); footprint OK for 3528, check polarity marks against chosen parts |
| D5 | SS34 — **DNP** (TPS61023 is synchronous; footprint kept as cheap insurance, review fix g) | `Diode:SS34` (stock, derived from SB120) | `Diode_SMD:D_SMA` | stock, resolves |
| D6 | SS14 (charge-pad reverse block) | `Diode:SS34` (same stock Schottky symbol, Value=SS14) | `Diode_SMD:D_SOD-123` | stock, resolves; 1 A SOD-123 Schottky is plenty for the ~200 mA charge current |
| CP1,CP2 | Magnetic charge pads (5 V in) | `Connector_Generic:Conn_01x01` | `puck:EC_Electrode_2x8mm` | **PLACEHOLDER** — real footprint authored at layout time to match the purchased magnetic pogo cable's pad geometry (pitch + pad Ø measured from the actual cable) |
| L2 | NFC PCB coil | `Device:L` | *(none)* | etched spiral drawn at layout — deliberately no footprint |
| C12,C13 | NFC tuning (300 pF placeholder) | `Device:C` | same 0603 HandSolder | stock, resolves; exact values computed from the drawn spiral at layout, matched NP0 |
| Q1–Q5 | AO3400A (Q1–Q3 were 2N7002 — review M5; all four LED/heater/piezo FETs now one BOM line; Q5 = piezo low-side switch, review M2) | `Transistor_FET:AO3400A` | `Package_TO_SOT_SMD:SOT-23_Handsoldering` | stock, resolves; `Transistor_FET:2N7002` no longer used |
| L1 | **1 µH** power inductor ≥2 A sat (was 22 µH — TPS61023 wants 0.37–2.9 µH, SLVSF14B §8.2.2.2) | `Device:L` | `Inductor_SMD:L_Sunlord_SWPA4030S` | **PLACEHOLDER** — stock 4×4×3 mm shielded footprint (Sunlord is routinely JLC-stocked); real 1 µH part selected at BOM time, swap footprint if it differs |
| C1,C2 | **4.7 µF X7R 0805** EC coupling (was 100 nF — review C4) | `Device:C` | `Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder` | stock, resolves; X7R + 0805 to limit DC-bias derating |
| C7–C11,C16 | 100 nF (C16 = EC bias tap, review C3) | `Device:C` | `Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder` | stock, resolves |
| C14,C15,C17 | 1 µF (U10 LDO in/out; U9 mic bulk) | `Device:C` | same 0603 HandSolder | stock, resolves |
| C3 | 100 µF MLCC | `Device:C` | `Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder` | stock; MLCC → non-polarized `Device:C` symbol |
| C5,C6 | 22 µF **16 V 0805** (was 0603 — 50–70 % DC-bias derate at 5 V) | `Device:C` | `Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder` | stock, resolves; check DC-bias curve at BOM time |
| R1,R2,R14,R17 | 4.7 k | `Device:R` | `Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder` (all small R below use this) | stock, resolves |
| R3 | 1 k · R4,R8–R10,R12 100 k · R5 220R · R6 360R · R7 150R · R13 220R · R15 750k · R16 100k (TPS61023 FB — math below) · R18,R19 5.1k | `Device:R` | same 0603 HandSolder | stock, resolves |
| R20–R24,R26,R27 | 1 MΩ (R20/R21 EC mid-rail divider, R22/R23 force-electrode bias legs — review C3; R24 piezo bleed — review M2; R26/R27 bias legs for the 4-wire sense nodes AIN2/AIN3 — review-C3 logic, added 2026-08-31) | `Device:R` | same 0603 HandSolder | stock, resolves |
| R11 | 100 Ω 1 W heater (2512) | `Device:R` | `Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder` | stock, resolves; was axial THT 2 W — SMD 2512 1 W chosen for the integrated board |
| E1,E2 | EC inner **sense** electrodes (4-wire; sensed on AIN2/AIN3) | `Connector_Generic:Conn_01x01` | `puck:EC_Electrode_2x8mm` (custom) | copper feature |
| E3,E4 | EC outer **force** electrodes (4-wire upgrade 2026-08-31; EC_DRV drives these; 2-electrode fallback uses only this pair) | `Connector_Generic:Conn_01x01` | `puck:EC_Electrode_2x8mm` (custom) | copper feature |
| D7 | 275 nm UVC LED — **DNP, v2 channel** | `Device:LED` | `LED_SMD:LED_Cree-XP` (stock 3.45×3.45 mm — the "3535" class UVC emitters use; pads 1/2 + thermal pad 3, thermal unmatched by the 2-pin symbol → expected "extra pad" note at PCB update, fine for DNP) | exact emitter + footprint re-verified at v2 populate |
| PD1 | GUVC-T21GH UVC photodiode — **DNP, v2 channel** | `Connector_Generic:Conn_01x03` (part is a 3-lead amp module — Vcc/Vout/GND — not a bare 2-pin photodiode, so `Device:D_Photo` doesn't fit) | `Package_TO_SOT_THT:TO-5-3_Window` (stock; DigiKey lists the part as TO-205AA / TO-5-3) | datasheet on file `../../docs/datasheets/guvc-t21gh.pdf`: TO-5 can Ø8.1/9.1 mm flange, integrated TI amp, VCC 1.8–5.5 V, Vout 0.355 V per mW/cm², rise 3 ms. **Verify lead-vs-tab numbering against the physical can before v2 populate** |
| R25 | D7 series resistor — **DNP**, value sized at v2 | `Device:R` | same 0603 HandSolder | stock, resolves |
| PZ1 | Piezo disc 20–27 mm | `Device:Buzzer` | `TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm` ×2 as wire pads | 3D: `lib/3dmodels/Piezo_ABLF2722A.step` |
| TP1–TP18 | Test points (incl. 5V, BOOST_EN, **TP18 VBUS** — review minor: USB dead without the module VBUS pad fed, SWD ×5) | `Connector:TestPoint` | `TestPoint:TestPoint_Pad_D1.5mm` | stock, resolves |
| FDC1,FDC2 | FDC sense pads (FDC2 = CIN2 second pad at a different radius, added 2026-08-31) | `Connector_Generic:Conn_01x01` | `puck:FDC_Sense_Pad_10mm` (custom) | copper features |
| H1–H3 | M2 mounting holes | `Mechanical:MountingHole` | `MountingHole:MountingHole_2.2mm_M2` | stock, resolves |

### Placeholder footprints needing a BOM-time decision
1. **L1** — `Inductor_SMD:L_Sunlord_SWPA4030S` stands in for "any 4×4 power inductor" (Sunlord
   picked because JLC routinely stocks the SWPA series); pick the actual JLC-stocked **1 µH
   ≥2 A-sat** part and swap the footprint to match.
2. ~~U9 PDM mic~~ — **RESOLVED 2026-08-31**: exact part is now the IM69D130; stock symbol
   `Sensor_Audio:IM69D130` + stock footprint `Sensor_Audio:Infineon_PG-LLGA-5-1`, both verified
   against the Infineon datasheet on file. (Check JLC/LCSC stock at BOM time; if unstocked it is
   a DigiKey hand-place part — LLGA is hot-air friendly.)
3. **D1–D3 LEDs** — 3528 Everlight footprint is a stand-in until exact LCSC emitters are chosen
   (365 nm authenticity check!). Confirm anode/cathode pad convention per part.
4. **CP1/CP2 charge pads** — `puck:EC_Electrode_2x8mm` is a stand-in only; the real footprint is
   authored at layout time once the magnetic pogo cable is in hand (measure its pad pitch and
   diameter, mask-open ENIG pads like the EC electrodes).
5. ~~U1 E73 footprint inner-row pads~~ — moot since the E73 was retired (2026-08-30); the
   MDBT50Q footprint is 61-pad verified (below).

## TPS61023 / LSM6DSO — authored-symbol verification notes (2026-08-31)

- **`puck-extra:TPS61023`** — authored from scratch (no stock symbol in KiCad 10.0.3).
  Pin table transcribed from TI datasheet **SLVSF14B** (downloaded from ti.com →
  `../../docs/datasheets/tps61023.pdf`, verified real PDF), Figure 5-1 / Pin Functions:
  **1 FB, 2 EN, 3 VIN, 4 GND, 5 SW, 6 VOUT** — DRL package = 6-pin SOT-563, stock footprint
  `Package_TO_SOT_SMD:SOT-563` (ships with a STEP model).
  - **FB divider math (R15/R16):** VOUT = VREF × (1 + R15/R16); VREF = **0.595 V typ**
    (PWM mode, DS §6.5 electrical characteristics: 580–610 mV). Chosen R15 = 750 kΩ,
    R16 = 100 kΩ → VOUT = 0.595 × 8.5 = **5.06 V** (target 5.0–5.1 V ✓). DS §8.2.2.1 wants
    R16 < 300 kΩ (FB leakage ≤ 20 nA → error ≪ 1 %); divider drain ≈ 6 µA and only while the
    rail is up (true load disconnect when EN low, IVOUT leakage ≤ 3 µA). Worst case over the
    ±2.5 % reference: 4.93–5.19 V — LED resistors unaffected at this precision.
  - **EN thresholds:** VEN_H ≥ 1.2 V, VEN_L ≤ 0.45 V (DS §6.5) — drivable from the 3.3 V rail
    *and* the pre-UICR 1.8 V rail.
  - **Inductor:** DS §8.2.2.2 — designed for 0.37–2.9 µH effective → L1 changed 22 µH → 1 µH.
- **`puck-extra:LSM6DSO`** — no stock LSM6DSO symbol (only LSM6DS3/DSL/DSM). Authored as a
  byte-copy of stock `Sensor_Motion:LSM6DSM` renamed, with Datasheet/Description fields updated.
  All 14 pins verified identical between the LSM6DSM symbol and the **LSM6DSO datasheet DS12140
  Table 1** (downloaded via SparkFun CDN mirror — st.com blocks direct download →
  `../../docs/datasheets/lsm6dso.pdf`, 172 pp, verified real PDF): 1 SDO/SA0, 2 SDx, 3 SCx,
  4 INT1, 5 VDDIO, 6 GND, 7 GND, 8 VDD, 9 INT2, 10 OCS_Aux, 11 SDO_Aux, 12 CS, 13 SCL, 14 SDA.
  I2C address DS §5.1.1: SA0→GND = 1101010b = **0x6A** (write D4h / read D5h). Package LGA-14
  2.5×3×0.83 mm P0.5 → stock `Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` (ships with
  a STEP model).
- **U9 IM69D130 (stock symbol, recorded here for the swap):** stock `Sensor_Audio:IM69D130`
  (derives from IM69D120 — same pinout) matches Infineon datasheet Table 7 exactly; footprint
  `Sensor_Audio:Infineon_PG-LLGA-5-1` is KiCad's StepUp-generated footprint from Infineon's own
  PG-LLGA-5-1 package page (the IM69D130's package). PDM spec: fclock 0.4–3.3 MHz, duty
  40–60 % below 2.65 MHz → the Adafruit-core default 1.032 MHz clock is **in spec** (the
  MP34DT06J undefined-region finding M7 is closed by the part swap). SNR trade: 66 dB(A) at
  1.536 MHz vs 69 dB(A) at 3.072 MHz — fine for slosh/fizz classification.

## MDBT50Q-1MV2 — verification notes (new U1, 2026-08-30)

- **Datasheet:** downloaded from raytac.com (`download/index.php?index_id=43`, direct PDF, 73 pp) →
  saved `../../docs/datasheets/mdbt50q-1mv2.pdf`. Module 10.5 × 15.5 × 2.05 mm (W tol −0.15/+0.20),
  chip antenna at one short edge, 61 pins: castellations on 3 sides + 6 bottom-center pads (56–61)
  + staggered inner rows. No thermal pad on this variant.
- **Footprint** `puck:MDBT50Q-1MV2` — byte-copy of stock `RF_Module:Raytac_MDBT50Q` (KiCad 10.0.3,
  KLC-reviewed) with only the internal name + 3D model path changed. Verified numerically against
  datasheet §2.2 recommended solder-pad drawing (p. 10): **all 61 pad centers match exactly
  (0 mismatches, < 0.001 mm)** after frame transform (datasheet origin bottom-left → KiCad centered);
  all pads 0.6 × 0.4 mm as specified ("x61 pad 0.6x0.4mm"). Pitches: bottom outer row 0.8 mm,
  side outer rows 0.8 mm staggered with inner rows, mid-row 56–61 at 0.8 mm. Bottom + mid-row pads
  are rotated 90° in the footprint (long axis ⊥ board edge — KLC convention; centers still exact).
- **Antenna keep-out** built into the footprint, matching datasheet §2.2/§2.3: all-copper-layer
  keep-out strip x −6.2…+6.2, y −7.75…−4.0 (the 3.8 mm antenna band, wider than the module) plus a
  top-layer-only 1.6 × 1.2 mm patch at x −2.3…−0.7 (the "toplayer no ground pad" at the antenna
  feed, 2.95 mm from module left edge). Datasheet still wants the no-ground zone "as wide as
  possible" on every layer and the module at the board edge — honor at layout.
- **Symbol** `puck-extra:MDBT50Q-1MV2` — copied from stock `RF_Module:MDBT50Q-1MV2` (same KiCad
  release), Footprint field repointed to `puck:MDBT50Q-1MV2`. All 61 pin numbers/names re-checked
  1:1 against datasheet §2.5 (pp. 14–17): 5×GND (1,2,15,33,55), VDD 28, VDDH 30, DCCH 31, VBUS 32,
  D−/D+ 34/35, SWDIO/SWDCLK 51/53, P0.18/nRESET 40, NFC1/NFC2 = P0.09/P0.10 on 52/54, 48 GPIO total.
- **Spec pin-map check (2026-08-30): every pin in the spec's map is exposed** — P0.02/P0.03 (AIN0/1),
  P0.06, P0.08, P0.09/P0.10 (NFC), P0.13–P0.17, P0.19–P0.21, P0.24–P0.29, D±, SWD, RESET (P0.18),
  VDDH, VDD. No remap needed (unlike the E73). Caveats: datasheet §2.6 restricts the "near-radio"
  pins (P0.02/P0.03/P0.28–P0.31, P1.01–P1.15, P0.09/P0.10) to standard-drive, **low-frequency I/O
  ≤ 10 kHz** — fine for EC_A/EC_B (analog SAADC) and NFC. **Pin-move executed at the
  2026-08-31 review follow-up:** EC_DRV_LO/HI moved P0.28/P0.29 → **P0.22/P0.23** (§2.5
  pins 46/45: exposed, full-drive, only a QSPI "recommended usage" note — no electrical
  restriction, same class as P0.19/P0.21). P0.28/P0.29 (AIN4/AIN5) are spares again.
  Also verified exposed for the follow-up batch: **P0.04/AIN2 (pin 20), P0.05/AIN3 (pin 21)**
  (EC 4-wire sense pair — full GPIO, no low-frequency note), **P0.11 (pin 27)** (UVC_EN,
  full-drive, TRACEDATA2 alt only), **P0.31/AIN7 (pin 12)** (UVC_PD — low-frequency pad,
  fine as analog input). Caveat kept on record: P1.01 (pin 61) and all exposed P1.xx except
  P1.00 are low-frequency-only — don't promote them to drive duty.

## E73-2G4M08S1C — verification notes (RETIRED 2026-08-30 — replaced by MDBT50Q-1MV2; kept for reference)

- Sources: EBYTE user manual (downloaded from cdebyte.com, `pdf-down.aspx?id=3866`) — 13×18 mm,
  43 stamp/castellated pads, 1.27 mm pitch, ceramic antenna at one short edge (keep-out!).
- Symbol pin map transcribed from the manual's §3 pin table and cross-checked against the
  cdebyte.com online pin definition — both agree on all 43 pins
  (19=VDD, 23=VDDH, 25=DCCH, 27=VBUS, 29/31=D∓, 26=P0.18/RESET, 37/39=SWDIO/SWDCLK,
  41/43=P0.09/P0.10 NFC, GND=5/21/24, rest GPIO).
- **Spec pin-map caveat (wiring time):** the spec's "proposed" pin map uses P0.27, P0.14, P0.16,
  P0.19, P0.21, P0.25 — **none of these are exposed on the E73**. Remap at schematic wiring
  (plenty of spare exposed GPIO: P0.04–P0.08, P0.12, P0.22, P1.xx…). SDA on P0.26 is fine.

## Custom footprints (`puck-parts.pretty`)

- **`EC_Electrode_2x8mm`** — single SMD pad #1, 2.0 × 8.0 mm, `F.Cu`+`F.Mask` with
  `solder_mask_margin 0.051` → mask-defined opening (fully exposed ENIG). No paste.
- **`CHG_Pad_D2.0mm`** (added 2026-08-31, dock delta) — single circular SMD pad #1,
  Ø2.0 mm, same `F.Cu`+`F.Mask`/no-paste ENIG style as the electrode; used ×4 for the
  magnetic dock constellation CP1–CP4 (GND/D−/D+/5V @ 2.54 mm pitch, Adafruit 5412
  cable geometry — final pad spacing verified against the physical cable at layout).
- **`FDC_Sense_Pad_10mm`** — single SMD pad #1, 10 × 10 mm, `F.Cu` only → stays under mask.
- Both validated with `kicad-cli fp upgrade` + `fp export svg`; E73/SnapEDA imports validated
  the same way.

## puck-extra additions (2026-08-31, dock delta)

- **U11 `puck-extra:USBLC6-2SC6`** — flattened copy of the stock KiCad
  `Power_Protection:USBLC6-2SC6` (derived from USBLC6-2P6), kept project-local so the
  schematic embed and library stay byte-identical (no `lib_symbol_mismatch` ERC noise).
  Footprint `Package_TO_SOT_SMD:SOT-23-6` (hand-solderable). Pins 1/6 = I/O1, 3/4 = I/O2,
  5 = VBUS, 2 = GND (all passive in the symbol).
- **FDC1004 SHLD1 (pin 1) / SHLD2 (pin 6) pin type corrected Input → Output** — they are
  the chip's active guard drivers (TI datasheet); the SnapEDA import had them as inputs,
  which made ERC flag the intentionally label-only SHLD1 guard net as undriven.

## 3D models

**Full audit done (KiCad 10.0.3):** every stock footprint in the parts table was checked against
the shipped `SharedSupport/3dmodels/` tree. Resolving fine: SOT-23-5/-23, TO-92_Inline,
JST-PH horizontal (J1), D_SMA, D_SOD-123, L_Sunlord_SWPA4030S, all 0603/0805/1210/2512 R+C.
Re-checked 2026-08-31 for the review swaps: **SOT-563 (U2) and LGA-14_3x2.5mm…3x4y (U8) both ship
with STEP models — resolve fine.** `Infineon_PG-LLGA-5-1` (U9) references a STEP KiCad does NOT
ship — same class of gap as the three below (tiny part; add a project-local copy with a model
only if the render matters). **Three stock footprints reference STEP files that KiCad does NOT
ship:** `AMS_OLGA-8_2x3.1mm_P0.8mm` (U3), `LED_Everlight-SMD3528…67-21ST` (D1–D3), and
`USB_C_Receptacle_HRO_TYPE-C-31-M-12` (J2). Since the stock libs can't be edited, those three
footprints now have **project-local copies in `puck-parts.pretty`** with models attached — see
the footprint-field switch note below. TestPoint/MountingHole footprints have no model reference
by design (nothing to render). CP1/CP2, E1–E4 and the FDC1/FDC2 sense pads are **copper
features** — they render as gold/mask pads natively; no models by design. The 2026-08-31
DNP-v2 additions (`LED_SMD:LED_Cree-XP` for D7, `Package_TO_SOT_THT:TO-5-3_Window` for PD1)
were **not** part of the model audit — DNP footprints, render cosmetics only; check at v2.

Downloaded (SnapEDA/vendor) in `lib/3dmodels/`: `MS5837-02BA.step`, `FDC1004DGSR.step`,
`Piezo_ABLF2722A.step`, plus the XIAO + AS7341-breakout models from the superseded carrier design.
Hand-authored VRML (KiCad convention, 1 unit = 2.54 mm) also in `lib/3dmodels/`:

- `E73-2G4M08S1C.wrl` — 18.16 × 13.21 mm green module PCB + silver RF shield (~70% coverage) +
  ceramic chip-antenna block at the bare +X end; matches the footprint outline exactly.
- `AS7341_OLGA-8.wrl` — 2 × 3.1 × 1 mm dark body + lighter optical window on top.
- `LED_PLCC2_3528.wrl` — 3.5 × 2.8 × ~1.9 mm white PLCC-2 body + translucent lens hint
  (one model shared by D1–D3; lens color not per-LED on purpose).

Attached to the `.pretty` source footprints (render-verified flush + centered on a scratch board):

| Footprint | Model (`${KIPRJMOD}/lib/3dmodels/…`) | offset (xyz, mm) | rotate (xyz, °) |
|---|---|---|---|
| `puck:MDBT50Q-1MV2` | `MDBT50Q-1MV2.step` (copied from KiCad 10.0.3 stock `RF_Module.3dshapes/Raytac_MDBT50Q.step`) | 0 0 0 | 0 0 0 |
| `puck:XDCR_MS583702BA01-50` | `MS5837-02BA.step` | 0 0 2.74 | 0 0 0 |
| `puck:SOP50P490X110-10N` | `FDC1004DGSR.step` | 0 0 0 | -90 0 0 |
| `puck:E73-2G4M08S1C` | `E73-2G4M08S1C.wrl` | 0 0 0 | 0 0 0 |
| `puck:AMS_OLGA-8_2x3.1mm_P0.8mm` (new copy of stock) | `AS7341_OLGA-8.wrl` | 0 0 0 | 0 0 0 |
| `puck:LED_Everlight-SMD3528_3.5x2.8mm_67-21ST` (new copy of stock) | `LED_PLCC2_3528.wrl` | 0 0 0 | 0 0 0 |
| `puck:USB_C_Receptacle_HRO_TYPE-C-31-M-12` (new copy of stock) | `TYPE-C-31-M-12.step` (**file not yet present** — see below) | 0 0 0 | 0 0 0 |

**Footprint-field switch (do in the schematic GUI, 4 refs):** to pick up the models, repoint the
Footprint fields of U3 → `puck:AMS_OLGA-8_2x3.1mm_P0.8mm`, D1–D3 →
`puck:LED_Everlight-SMD3528_3.5x2.8mm_67-21ST`, J2 → `puck:USB_C_Receptacle_HRO_TYPE-C-31-M-12`,
then "Update PCB from Schematic". The copies are byte-identical to the stock footprints except
for the model path, so pads/courtyards don't move.

**Get these yourself (login-walled):** J2 USB-C real STEP — a box model would look worse than
nothing for the curved shell, so download the vendor model from SnapEDA
(<https://www.snapeda.com/search/?q=TYPE-C-31-M-12>, free account) and save it as
`lib/3dmodels/TYPE-C-31-M-12.step`. The footprint copy already points at that path; it lights up
as soon as the file exists.

**Verification renders:** `renders/mdbt50q-check-top.png` / `renders/mdbt50q-check-iso.png` —
MDBT50Q-1MV2 STEP render-verified 2026-08-30 on a scratch board outside the repo (`kicad-cli pcb
render`): body flush and centered on the courtyard, shield over the pad area, chip antenna at the
pad-free end over the keep-out — no offset/rotation needed. Also `renders/model-check-top.png` and `renders/model-check-iso.png` — one
of every footprint used by the design, rendered with `kicad-cli pcb render` from a scratch board
(kept outside the repo). Everything shows a body except J2 (pending the SnapEDA STEP) and the
by-design bare copper features / test points / mounting holes.

Note: the copies of these footprints already placed in `puck-carrier.kicad_pcb` predate the model
attachment — run "Update PCB from Schematic" with *Update/re-import footprints* enabled (or
re-import the parts) so the board copies inherit the models and the Task-A footprint swaps.

## Superseded (XIAO carrier v1) — kept for the bench mule

`puck:XIAO-nRF52840-SMD` symbol + `puck:XIAO-nRF52840-{SMD,DIP}` footprints remain in the project
libs, verified as before (pads 1–14 castellated at 2.54 mm pitch, bottom pads 15–22 incl. VBAT/NFC;
3D model aligned <0.1 mm). Breakout-header rows (old J2–J5) are gone from the schematic — the
breakouts are bench hardware now, not board parts.


- **J2 USB-C 3D model**: `lib/3dmodels/TYPE-C-31-M-12.step` (SnapEDA, user-downloaded 2026-08-30) attached with offset (0,0,0), **rotate (-90, 0, 0)** — alignment render-verified (flush seating, pins on pad row, mouth outboard). Download task CLOSED.

## Block 10b additions (2026-08-31) — glow ring parts

- **`puck:LED_XL-1010RGBC` footprint** (new, project-authored): XINGLIGHT
  XL-1010RGBC-WS2812B, 1.0×1.0×0.8 mm, 4 corner pads. Land pattern taken from the
  datasheet's "Recommended Soldering Pattern" (p. 11): pads 0.45 × 0.40 mm, 0.4 mm
  gaps both axes → centers at (±0.425, ±0.40). Datasheet fetched from LCSC
  (part C5349953) and saved as `docs/datasheets/xl-1010rgbc.pdf` (18 pp, verified
  genuine). Pin-1 (DOUT) silk dot at top-left. **Order-time check**: confirm the
  polarity mark on the physical reel and run the JLC footprint check before
  placement — the datasheet's orientation-mark drawing is small.
- **`puck-extra:XL-1010RGBC` symbol** (new, embedded + in lib): graphics cloned from
  stock `LED:WS2812B`, **pins renumbered to the XL-1010 datasheet**: 1=DOUT, 2=VDD,
  3=GND, 4=DIN. The stock WS2812B symbol uses 1=VDD, 2=DOUT — using it with a
  datasheet-numbered footprint would swap VDD onto the DOUT pad. Do NOT swap back
  to the stock symbol without renumbering the footprint pads to match.
- **P1.00 (`RING_DATA`) verification**: `docs/datasheets/mdbt50q-1mv2.pdf` §2.5,
  pin 47 — exposed castellation, "(recommended usage: QSPI)" only, no
  "standard drive, low frequency I/O only" note → full-speed, fine for the
  800 kHz WS2812B data stream. No pin substitution was needed.
- D8 status LED uses stock `LED_SMD:LED_0603_1608Metric`; D9 uses the existing
  `Diode:SS34` symbol (value "1N5819WS/SS14 ring supply") on `Diode_SMD:D_SOD-123`;
  C18–C23 on the 0603 HandSolder cap footprint. Ring LEDs LCSC C5349953 (extended,
  JLC-placed; alt SK6805-EC15 C2890035 decided at order time per spec parts list).
