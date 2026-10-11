# Wiring Guide — puck-carrier schematic (103 symbols, post-review)

Wire block by block, in this order. Use **global labels** (exact names below) —
short stub off the pin, label on the stub. Don't draw long wires between blocks.
After each block: save, glance at ERC count going down.

## Global labels (the complete net list — type exactly)

Rails: `VBAT` `3V3` `1V8` `5V` `GND` `VBUS`
Digital: `SDA` `SCL` `OW_DQ` `LED_WHITE` `LED_850` `LED_365` `HEATER_EN`
`PIEZO` `BOOST_EN` `IMU_INT` `PDM_CLK` `PDM_DATA` `UART_TX` `UART_RX`
`UVC_EN` `SWDIO` `SWCLK` `RESET` `USB_DP` `USB_DM` `NFC1` `NFC2` `CHG_STAT`
`LED_STAT` `RING_DATA` `BTN_DFU` `BTN_FRESET`
Analog: `EC_A` `EC_B` `EC_SENSE_A` `EC_SENSE_B` `EC_BIAS` `EC_DRV_LO`
`EC_DRV_HI` `UVC_PD` `SHLD1`

## Block 1 — Brain (U1 MDBT50Q-1MV2)

Label every used pin per the spec pin map (spec §Pin map is the authority; the
symbol has real P0.xx names so this is mostly reading):

- VDDH (30) → `VBAT` · VDD (28) → `3V3` · all 5 GND pins → `GND`
- VBUS (32) → `VBUS` · D+ (35) → `USB_DP` · D− (34) → `USB_DM`
- SWDIO (51) → `SWDIO` · SWDCLK (53) → `SWCLK` · P0.18 (40) → `RESET`
- P0.26 → `SDA` · P0.27 → `SCL`
- P0.02 → `EC_A` · P0.03 → `EC_B` · P0.04 → `EC_SENSE_A` · P0.05 → `EC_SENSE_B`
- P0.22 → `EC_DRV_LO` · P0.23 → `EC_DRV_HI`
- P0.13/14/15 → `LED_WHITE` / `LED_850` / `LED_365`
- P0.16 → `OW_DQ` · P0.17 → `HEATER_EN` · P0.19 → `PIEZO` · P0.20 → `BOOST_EN`
- P0.21 → `IMU_INT` · P0.08 → `PDM_CLK` · P0.06 → `PDM_DATA`
- P0.24 → `UART_TX` · P0.25 → `UART_RX` · P0.11 → `UVC_EN` · P0.31 → `UVC_PD`
- P0.07 → `CHG_STAT`
- P0.09 → `NFC1` · P0.10 → `NFC2`
- **DCCH (31): no-connect X** (spec rule — never fit the LC, never set DCDCEN0)
- Every remaining unused pin: no-connect X (P0.00/01/12/28/29, P1.xx, etc.)
- C3 100 µF: `3V3` ↔ `GND` (place near U1 in layout later)

## Block 2 — Battery + charging + magnetic dock (USB-C REMOVED 2026-08-31)

- J1: pin 1 → `VBAT`, pin 2 → `GND`
- U7 MCP73831 (SOT-23-5): 1 STAT → `CHG_STAT` (→ U1 P0.07; open-drain,
  FW pull-up) · 2 VSS → `GND` · 3 VBAT → `VBAT` · 4 VDD → `VBUS` ·
  5 PROG → R17 4.7 k → `GND`
- **Dock pad constellation** (row order GND / D− / D+ / 5V, Ø2.0 mm pads @
  2.54 mm pitch — copies the Adafruit 5412 magnetic data cable):
  - CP1 "PAD_GND" → `GND`
  - CP2 "PAD_DM" → R29 27 Ω → `USB_DM`
  - CP3 "PAD_DP" → R30 27 Ω → `USB_DP`
  - CP4 "PAD_5V" → D6 anode; D6 cathode → `VBUS`
  (All pads dead when undocked: D6 blocks the rail; the nRF USB PHY is
  VBUS-powered so D± sit at 0 V without the dock.)
- U11 USBLC6-2SC6 ESD array: datasheet-standard USB circuit — VBUS pin →
  `VBUS`, GND pin → `GND`, I/O pairs across D+/D− on the PAD side of R29/R30
- TP18 → `VBUS` · TP19 → `UART_TX` · TP20 → `UART_RX`
- J2 / R18 / R19: REMOVED from the design (delete if present)

## Block 3 — Boost (U2 TPS61023, SOT-563)

Pinout: 1 FB · 2 EN · 3 VIN · 4 GND · 5 SW · 6 VOUT

- VIN (3) → `VBAT`, with **C5 22 µF `VBAT`↔`GND`** as the input cap
  (C5 = input, C6 = output — that's the intended split of the pair)
- `VBAT` → L1 (1 µH) → SW (5)
- VOUT (6) → `5V`, with C6 22 µF `5V`↔`GND`
- FB (1) → junction of R15 750 k (up to `5V`) and R16 100 k (down to `GND`)
- EN (2) → `BOOST_EN` · GND (4) → `GND`
- D5 (DNP insurance): anode → SW node, cathode → `5V` (wire it; just never
  populate unless the TPS61023 disappoints)

## Block 4 — I2C sensors

- R1: `SDA` → `3V3` · R2: `SCL` → `3V3` (the bus's only pull-ups)
- U10 XC6206 (1 GND · 2 VOUT · 3 VIN): VIN → `3V3` + C14 1 µF to `GND`;
  VOUT → `1V8` + C15 1 µF to `GND`; GND → `GND`
- U3 AS7341: **VDD → `1V8`** (never 3V3 — this is the review's #1 catch) +
  C7 100 nF at the pin; GND → `GND`; SDA/SCL → bus; **GPIO → `GND`**
  (not 3.6 V-tolerant); INT, LDR → no-connect
- U4 FDC1004: VDD → `3V3` + C8 100 nF; GND → `GND`; SDA/SCL → bus;
  CIN1 → wire to the FDC1 pad symbol; CIN2 → FDC2 pad symbol;
  CIN3, CIN4 → no-connect (no stubs — leave them bare X's);
  SHLD1 → `SHLD1` (also label both pad-adjacent guard notes); SHLD2 → no-connect
- U5 MS5837: VDD → `3V3` + C9 100 nF; GND → `GND`; SCL/SDA → bus
- U8 LSM6DSO: VDD and VDDIO → `3V3` + C10 100 nF; GND → `GND`; SDA/SCL → bus;
  **SDO/SA0 → `GND`** (addr 0x6A) · **CS → `3V3`** (I2C mode) ·
  INT1 → `IMU_INT` · INT2 → no-connect

## Block 5 — Mic (U9 IM69D130)

VDD → `3V3` + C11 100 nF + C17 1 µF · GND → `GND` · CLK → `PDM_CLK` ·
DATA → `PDM_DATA` · SELECT → `GND` (mono/left)

## Block 6 — 1-wire (U6 DS18B20, TO-92: 1 GND · 2 DQ · 3 VDD)

GND → `GND` · DQ → `OW_DQ` + R14 4.7 k → `3V3` · VDD → `3V3`

## Block 7 — EC front end (the careful one — follow exactly)

Drive path:
- `EC_DRV_LO` → R3 1 k → node **D** ← R4 100 k ← `EC_DRV_HI` (R3/R4 outputs join)
- node D → C1 4.7 µF → **force node A** = E3 pad = label `EC_A`
- **force node B** = E4 pad = label `EC_B` → C2 4.7 µF → `GND`

Sense pair (4-wire):
- E1 pad → `EC_SENSE_A` · E2 pad → `EC_SENSE_B` (nothing else on these nets
  except their bias legs below — they must stay high-impedance)

Bias network (SAADC inputs must never float):
- `3V3` → R20 1 MΩ → tap node = label `EC_BIAS` → R21 1 MΩ → `GND`
- `EC_BIAS` → C16 100 nF → `GND`
- `EC_BIAS` → R22 1 MΩ → `EC_A` · `EC_BIAS` → R23 1 MΩ → `EC_B`
- `EC_BIAS` → R26 1 MΩ → `EC_SENSE_A` · `EC_BIAS` → R27 1 MΩ → `EC_SENSE_B`

## Block 8 — LED drivers (×3 identical, loads on `5V`)

Per channel: `5V` → Rseries → LED anode; cathode → Q drain; Q source → `GND`;
Q gate → control label **and** → Rpulldown 100 k → `GND`.
- D1 white: R5 220 Ω, Q1, R8, gate ← `LED_WHITE`
- D2 850 nm: R6 360 Ω, Q2, R9, gate ← `LED_850`
- D3 365 nm: R7 150 Ω, Q3, R10, gate ← `LED_365`

## Block 9 — Heater

`5V` → R11 100 Ω 2512 → Q4 drain; source → `GND`; gate ← `HEATER_EN` +
R12 100 k → `GND`

## Block 10 — Piezo

`3V3` → PZ1 pin 1; PZ1 pin 2 → R13 220 Ω → Q5 drain; Q5 source → `GND`;
Q5 gate ← `PIEZO`; R24 1 MΩ **across PZ1's two pins** (bleed).
*(On 3V3, not 5V, so the buzzer works with the boost off.)*
**Add while you're here: one 100 k gate pull-down on Q5's gate** (grab another
R from the Add Symbol dialog, call it R28, 0603 like R8–R10) — Q5 was added in
the review batch and is the only FET missing one. Two clicks now, one boot-time
chirp avoided.

## Block 10b — Status LED + glow ring (added 2026-08-31)

- D8 (0603 LED): P0.12 GPIO → R31 1 k → D8 anode; cathode → `GND` (net `LED_STAT`)
- Ring supply: `5V` → D9 Schottky → net `5V_RING`; each of D10–D15 (XL-1010):
  VDD → `5V_RING` + its own 100 nF (C18–C23) to `GND`; GND → `GND`
- Data chain: `RING_DATA` (P1.00 — verified 2026-08-31: datasheet §2.5 pin 47,
  QSPI-class, no low-freq restriction) → R32 220 Ω →
  D10 DIN; D10 DOUT → D11 DIN; … D14 DOUT → D15 DIN; D15 DOUT → no-connect

## Block 11 — NFC

L2 pin 1 → `NFC1` · pin 2 → `NFC2` · C12: `NFC1` → `GND` · C13: `NFC2` → `GND`
(values stay placeholder — computed at layout from the drawn spiral)

## Block 12 — UVC (DNP, wire it anyway so v2 is populate-only)

`5V` → R25 → D7 anode; D7 cathode → `UVC_EN` (GPIO low-side sink).
PD1 (TO-5, 3 leads): Vcc → `3V3` · Vout → `UVC_PD` · GND → `GND`.
*(Known v2 caveat, already documented: many 275 nm emitters have Vf > 5 V —
emitter choice at populate time must be a ≤5 V part or v2 revisits this. Not
today's problem.)*

## Block 13 — Test points, SWD, mech

- TP1–TP12 → each one's net is printed as its Value (3V3, GND, GND, SDA, SCL,
  EC_A, EC_B, EC_DRV_LO, EC_DRV_HI, VBAT, 5V, BOOST_EN)
- TP13–TP17 → `SWDIO` `SWCLK` `RESET` `3V3` `GND` (the SWD set) · TP18 → `VBUS`
- TP21/TP22 (added 2026-08-31) → `BTN_DFU` (P1.08) / `BTN_FRESET` (P1.09) —
  commissioning item 2's DFU-force pads; tweezer-to-GND, internal pull-ups
- FDC1/FDC2 pads, E1–E4 pads: already covered above. H1–H3 mounting holes
  REMOVED 2026-08-31 (shell-ledge retention instead; see spec parts list)
- PWR_FLAG — as built (2026-08-31): ×5 on `3V3`, `GND`, `VBUS`, `PAD_5V`,
  `5V_RING` (#FLG01–05). NO flag on `VBAT` — U7 pin 3 is a Power output and a
  flag there is a hard ERC conflict. `5V_RING` needs one because the ring LED
  VDD pins are power_in behind D9. `5V`/`1V8` need none (chip Power outputs).

## Endgame checklist

1. Annotation is already done (all refs assigned) — don't re-annotate.
2. ERC: work it to zero *meaningful* errors. Acceptable leftovers: single-pin
   nets on FDC1/FDC2/CP pads and electrode pads (they're real copper that
   leaves the board), and "input pin not driven" on DNP-part nets.
3. Save, close KiCad, then ping me for the **net-by-net review** — I'll diff
   the netlist against the spec pin map before you touch the PCB.
