# Water Puck — Integrated Board Spec (spin 1)

**The PCB is the puck.** One Ø46 mm circular 4-layer board, bare nRF52840 module,
sensors mounted directly, double-sided, dipped in epoxy after commissioning.
JLC assembles BOTH faces (2026-09-01: 0402 passives, LGA/VSSOP on the bottom);
hand-placed: U1 module, U5, J1, piezo/battery/NFC wires.

> **2026-08-31: design review applied.** This spec incorporates the full fix list
> from `../docs/design-review.md` (5 critical / 15 major confirmed findings).
> Part swaps: boost MT3608 → **TPS61023**, IMU LIS2DW12 → **LSM6DSO**, mic
> MP34DT06J → **IM69D130**; plus the 1.8 V LDO for the AS7341, the EC bias
> network, and the bootloader/commissioning gates below.
>
> **2026-08-31 review follow-up (free-copper batch):** EC upgraded to a
> **4-electrode cell** (E3/E4 force + E1/E2 sense on AIN2/AIN3; 2-electrode
> stays the firmware fallback); **FDC2** second capacitive pad on CIN2;
> **UVC organics channel** (D7/PD1/R25) as DNP v2 footprints; **EC drive moved
> P0.28/P0.29 → P0.22/P0.23** (old pins are ≤10 kHz low-frequency pads).

## Brain: bare module (replaces the XIAO)

- **U1: Raytac MDBT50Q-1MV2** (nRF52840, castellated, ~$11 DigiKey — same cart as the
  MS5837). Chosen for reliability over price (Paolo's call): best-documented module in
  the ecosystem, near-complete pin exposure, FCC/CE listed, huge proven install base
  (nice!nano-class boards). Rejected alternates: EBYTE E73-2G4M08S1C (~$5, weaker docs,
  retired 2026-08-30 — six spec pins not exposed), MinewSemi MS88SF3 (JLC-placeable but
  intermittent stock).
- Ships blank: **one-time SWD flash of a custom Adafruit nRF52 bootloader build**
  required (J-Link/DAP from the college lab or a $12 clone) — see the
  bootloader/commissioning section; **never flash a prebuilt hex** (NFC trap). After
  that: USB + BLE DFU as before.
- **SWD pads on the board** (SWDIO, SWCLK, GND, 3V3, RESET) — 5 test points or
  Tag-Connect pattern, bottom side, reachable before potting.
- IMU + mic are no longer free (they were XIAO Sense onboard parts): now board parts
  **U8 LSM6DSO** (I2C addr 0x6A: SDO/SA0 → GND, CS → VDDIO — no bus clash) and
  **U9 IM69D130** PDM microphone (PDM clock 0.4–3.3 MHz, so the nRF core default
  1.032 MHz is in-spec).
- No 32.768 kHz crystal on the module: the puck variant runs **`USE_LFRC`** (never
  copy the XIAO variant's `USE_LFXO` — the SoftDevice hangs at boot waiting for a
  crystal that isn't there). Frees P0.00/P0.01 as spare GPIO.
- **DCCH pad: leave unconnected**, and firmware must never set DCDCEN0 (no LC
  fitted — enabling it soft-bricks the board including debug access).

## Power architecture

- **BT1: protected LiPo pouch 400–500 mAh** (with protection PCB — buy protected cells)
  on **J1 JST-PH**. Battery → **module VDDH pin** (nRF52840 high-voltage mode, 2.5–5.5 V
  native — no LDO, no back-feed hacks). MDBT50Q-1MV2 exposes VDDH (pin 30); confirmed
  at review.
- **UICR REGOUT0 — critical commissioning step (review C2):** in VDDH mode the "3V3"
  rail is REG0's *output*, and REGOUT0's erased default is **1.8 V**. A blank module
  boots BLE but runs the whole sensor rail at 1.8 V (FDC1004 + DS18B20 dead, FET gates
  marginal) — and any `--eraseall` resurrects the trap. Three layers:
  1. One-time SWD flash includes `nrfjprog --memwr 0x10001304 --val 5` (REGOUT0=3V3)
     + pin reset, then **measure 3.3 V on the 3V3 pad** before any sensor bring-up.
  2. Puck variant init guard: if REGOUT0 reads default → NVMC write VOUT=3V3 →
     `NVIC_SystemReset()` (Nordic's standard pattern; protects against post-potting
     erase + DFU reflash).
  3. STATUS.md commissioning gate: "REGOUT0=3V3 verified (rail measures 3.3 V)";
     re-check after any eraseall.
- **Battery floor / rail accuracy (review M1):** REG0 needs VDDH ≥ VDD + 0.3 V and its
  output error is −10/+5 % (a 3.3 V setting can legally sit at 2.97 V — below the
  FDC1004/DS18B20 3.0 V floor). Policy: battery-empty defined at **VDDH ≈ 3.5–3.6 V**
  measured via the SAADC **VDDHDIV5** internal channel (free, no divider);
  bench-measure the actual REG0 output at commissioning (bump REGOUT0 if < 3.05 V);
  log VDD and VDDH/5 with every FDC1004/DS18B20 acquisition and **flag** (not discard)
  samples with VDD < 3.0 V as out-of-spec (rule 1). REGOUT0=3V0 remains a fallback
  option — decide against the measured discharge curve.
- **REG0 external-current budget / TX interlock (review M2):** external draw (GPIO +
  VDD pin) is limited to **25 mA at TX ≤ +4 dBm, only 5 mA above, 1 mA in System OFF**.
  Policy: default TX **0 dBm**, hard cap **+4 dBm** unless the radio-vs-load interlock
  guarantees all VDD loads quiescent during TX (store-and-forward already decouples
  sampling from sync — nearly free). DC/DC does *not* raise IEXT limits. The piezo is
  off the GPIO entirely (Q5 low-side switch, below). Written System OFF budget < 1 mA
  before layout — the PDM mic clock **must be stopped in System OFF** (650 µA running
  vs 5 µA off).
- **Charging: U7 MCP73831-2, fed two ways:**
  - **Magnetic charge pads (the potted unit's path):** two exposed hard-gold/ENIG pads
    on the bottom face + a potted alignment magnet; snaps onto a cheap 2-pin magnetic
    pogo cable (buy the cable FIRST — pad spacing copies its geometry). Garmin-dive-
    computer pattern: pads connect ONLY to the charger input through D6 Schottky (SS14)
    — zero volts on the pads when undocked, so no electrolysis/leaching path while
    submerged. Wipe pads before charging; charge dry.
  - **USB-C: REMOVED (2026-08-31, research-backed).** The dock IS the USB port now:
    the 4-pad constellation carries GND / D− / D+ / 5V (order fixed, copies the
    Adafruit 5412 magnetic data cable's geometry — Ø2.0 mm pads, 2.54 mm pitch,
    ENIG 2u"). D± → 27 Ω series (R29/R30) + USBLC6-2SC6 ESD (U11) → module USB pins;
    5V pad → D6 → VBUS net → module VBUS pad (pin 32) + charger. nRF USB PHY is
    VBUS-powered, so undocked/submerged the data pads sit at true 0 V — same
    zero-volts-in-water property as the charge pads. Reversal keying: **two magnets,
    opposite polarities out** (flipped cable repels); SS14 backstops any forced
    reversal. Full USB DFU + UF2 + CDC serial work on the dock. Research record:
    Garmin/Whistle/Fi precedents, plating and leaching analysis — see session notes.
  - R_prog 4.7 k ≈ 200 mA (~0.5 C). **STAT → CHG_STAT → P0.07** (open-drain,
    FW internal pull-up) — charge-present detect for the sleep-during-charging rule.
  - MCP73831 has no power path: firmware **sleeps (radio off, sensors idle) whenever
    charger power is detected** so termination sees true battery current.
- **U2: TPS61023 boost → 5 V rail** for LEDs + heater (replaces MT3608, review M4:
  **true output load disconnect** — no permanent VBAT→rail path, no FB bleed when off).
  - L1 **1 µH** shielded power inductor, ≥2 A sat (TPS61023 wants 0.37–2.9 µH
    effective — the MT3608-era 22 µH is out of range).
  - FB divider **R15 750 k / R16 100 k** → VOUT = 0.595 V × (1 + 750/100) ≈ **5.06 V**
    (VREF 0.595 V typ PWM, datasheet SLVSF14B §6.5; R16 < 300 k per §8.2.2.1; ~6 µA
    divider drain only while the rail is up).
  - C5/C6 **22 µF, 16 V, 0805** (0603 derates 50–70 % at 5 V bias); check the DC-bias
    curve at BOM time.
  - **D5 SS34: DNP** — the TPS61023 is synchronous; footprint kept as cheap insurance.
  - EN ← GPIO (`BOOST_EN`); EN VIH is 1.2 V min, so it works from both 3.3 V and the
    pre-UICR 1.8 V rail. Kept even with LiPo because a **constant 5 V rail = constant
    LED brightness** independent of battery state — the optical channels stay
    calibrated as the battery drains. No supercap needed (LiPo sources bursts directly).
  - Layout: hot loop tight and **diametrically opposite the BLE antenna sector**.
- **U10: XC6206P182MR 1.8 V LDO → AS7341 VDD only** (review C1: AS7341 abs max is
  **2.2 V** — at 3.3 V the bare chip is destroyed; every breakout carries this LDO).
  3V3 in, **C14/C15 1 µF** ceramic on LDO in/out (100 nF alone is marginal for XC6206
  stability); keep C7 100 nF at the U3 VDD pin on the 1V8 net. No level shifter — the
  AS7341 digital pins are 3.6 V-rated, so SCL/SDA/INT stay on the 3.3 V bus. ~1 µA Iq.
- **C3: 100 µF MLCC 1210** on VDD near the module (BLE burst buffer).
- GONE from the coin-cell design: supercap C4, JP1, D4 Schottky, coin holder.
- **Potting note (accepted risk):** LiPo in epoxy can swell with age. Mitigation:
  silicone-wrap the cell / pot its pocket in soft silicone, not hard epoxy;
  one-semester demo lifetime is the design target. Never pot an unprotected cell.

## Pin map (final — schematic netlist machine-verified against this table 2026-08-31; module pins are P0.xx/P1.xx)

| nRF pin | Net | Function |
|---|---|---|
| P0.26 / P0.27 | SDA / SCL | I2C: AS7341 0x39, FDC1004 0x50, MS5837 0x76, LSM6DSO 0x6A |
| P0.02 (AIN0) / P0.03 (AIN1) | EC_A / EC_B | differential SAADC on the **force pair** (E3/E4 nodes; RESP/RESN = Bypass — external bias network). 2-electrode fallback measures here |
| P0.04 (AIN2) / P0.05 (AIN3) | EC_SENSE_A / EC_SENSE_B | second differential SAADC pair on the **inner sense electrodes E1/E2** (4-wire mode; no current → fouling-immune). Datasheet §2.5 pins 20/21: exposed, full GPIO, no low-frequency restriction |
| P0.22 / P0.23 | EC_DRV_LO / EC_DRV_HI | 1 kΩ / 100 kΩ auto-range drive, high-drive H0H1. **Changed at review follow-up:** moved off P0.28/P0.29, which are standard-drive ≤10 kHz low-frequency pads (datasheet §2.6) — the 5–10 kHz low-range excitation was at the pad limit. P0.22/P0.23 (§2.5 pins 46/45) are exposed full-drive pads with only a "recommended usage: QSPI" note (no electrical restriction, per LIBRARIES.md). P0.28/P0.29 (AIN4/AIN5) freed back to spares |
| P0.13 / P0.14 / P0.15 | LED_WHITE / LED_850 / LED_365 | Q1–Q3 gates (loads on 5 V) |
| P0.16 | OW_DQ | DS18B20 1-wire, 4.7 k pull-up to 3V3 |
| P0.17 | HEATER_EN | Q4 gate |
| P0.19 | PIEZO | Q5 gate (low-side FET switch; piezo load off the GPIO) |
| P0.20 | BOOST_EN | TPS61023 EN |
| P0.21 | IMU_INT | LSM6DSO INT1 (tilt wake; INT default state re-checked before bootloader button pick) |
| P0.08 / P0.06 | PDM_CLK / PDM_DATA | microphone |
| P0.24 / P0.25 | UART_TX / UART_RX | debug, test points only |
| P0.07 | CHG_STAT | U7 STAT, open-drain, FW pull-up — charger-attached detect |
| P0.12 | LED_STAT | D8 bootloader/status LED (0603, basic part) + R31 1 k, active-high from 3V3 GPIO — the commissioning section's LED_PRIMARY, and matches the firmware variant's LED_BUILTIN placeholder |
| P1.00 | RING_DATA | 12× XL-1010RGBC-WS2812B addressable ring (D10–D21, 2026-09-01), top-face rim. Data 800 kHz → needs a full-speed pin: P1.00 **VERIFIED 2026-08-31** (mdbt50q datasheet §2.5, pin 47 castellation, "recommended usage: QSPI" only — NO low-frequency restriction; the ≤10 kHz limit applies to other pins) — wired as planned, no substitution. Ring VDD = 5V rail through D9 Schottky (≈4.6 V — fixes 3.3 V-logic VIH margin); 6× 100 nF decouplers (C18–C23); R32 220 Ω data series. Zero idle drain: the TPS61023 load-disconnect kills the ring entirely when the rail is down. FW rule: ring dark during optical acquisitions. |
| P1.08 | BTN_DFU | TP21 (SMD pad, east-rim column; restored 2026-09-04) — bootloader BUTTON_DFU, tweezer-to-GND forces DFU pre-potting (commissioning item 2). §2.5 pin 25: exposed, general-purpose, no restriction. Internal pull-up, no external parts |
| P1.09 | BTN_FRESET | TP22 (SMD pad, east-rim column; restored 2026-09-04) — bootloader BUTTON_FRESET, same scheme. §2.5 pin 26: exposed, general-purpose (TRACEDATA3 alt only) |
| P0.28 (AIN4) / P0.29 (AIN5) / P0.00 / P0.01 | EXP_A4 / EXP_A5 / EXP_00 / EXP_01 | Expansion pads TP23–TP26 (bottom east rim). AIN4/AIN5 also reach **E5/E6, two Ø3 mm gold aux pads on the sensor face** (2026-09-04): E5 = iridium-oxide-plated pH-change electrode (campus chem lab electrodeposition), E6 = bare-gold pseudo-reference; read differentially with TACQ 40 µs, log counts only, never absolute pH. Unpopulated experiment = harmless gold dots. |
| P0.11 / P0.31 (AIN7) | — (NC) | Reserved for the v2 UVC channel (UVC_EN / UVC_PD). D7/PD1/R25 were cut from spin 1 on 2026-09-01; pins are no-connect. |
| D+ / D− | USB | native USB → R29/R30 27 Ω → dock pads D+/D− (U11 ESD on pad side) |
| VBUS | VBUS | dock 5V pad → D6 → VBUS → module VBUS pad (pin 32) + U7 VDD + decoupling |
| SWDIO / SWCLK / RESET | SWD | programming pads (RESET = P0.18 via CONFIG_GPIO_AS_PINRESET) |
| — | SHLD1 | FDC1004 active guard net: pour behind the sense pad + guard traces on the CIN1 run |
| P0.09 / P0.10 | NFC1 / NFC2 | **NFC-A tag: OFF-BOARD coil (2026-09-04).** No PCB spiral fits at Ø46 (all four planes would need a ≥14 mm void). L2 = ferrite-backed 13.56 MHz flex antenna (or a hand-wound ~1 µH loop) on two SMD wire pads on the bottom face next to the module, stuck to the LiPo pouch with the ferrite toward the pouch; ≥5 mm from the BLE antenna sector and 3–5 mm from magnets/charge pads. C12/C13 300 pF are placeholders — retune to the antenna with magnet + battery installed. Tap-to-pair, tap-to-sync when the puck is out for washing. |

Glow-ring note: product-story UI (green/amber/blue/red) now has hardware.

pH policy (2026-09-04): no probes ever — a wire defeats the puck. Demo pH =
indicator-patch mode (colorimetric pH/NH3 badge over the optical cluster, read
by U3, firmware only). Experimental on-face pH-change electrode = E5/E6 above.
Glass/ISFET probes are out of scope for this project.

Everything on real GPIO. The four spares are brought out on **expansion pads
(2026-09-04)**: TP23 EXP_A4 = P0.28/AIN4, TP24 EXP_A5 = P0.29/AIN5, TP25 EXP_00 =
P0.00 (XL1, free under LFRC), TP26 EXP_01 = P0.01 (XL2) — 4 SMD pads 1.2×2.2 mm at
2 mm pitch on the bottom east rim; 3V3/GND on the SWD row. (P0.00/P0.01 freed by
LFRC; P0.28/P0.29 = AIN4/AIN5 freed by the EC-drive pin move. Spare-pool exits 2026-08-31:
P0.07 → CHG_STAT, P0.12 → LED_STAT, P1.00 → RING_DATA, and P1.08/P1.09 →
BTN_DFU/BTN_FRESET on TP21/TP22 — the bootloader button pick is now settled).

## Board outline

- **Ø46 mm circle** (Paolo's call 2026-08-31 — Ø40 was too cramped for 124 parts to look clean in clear resin; Ø46 gives the gold features breathing room, still palm-sized), 1.6 mm FR4, ENIG (electrodes), **4 layers: Sig / GND / PWR / Sig**
  (~$15 over 2-layer at this size; solid ground under EC ADC traces, mic, and the boost
  loop — with the planned exceptions: the FDC pad gets **SHLD1**, not GND, behind it,
  and the NFC coil + BLE antenna zones are copper voids on all layers).
- **EC electrodes: ON-FACE, no tongue (Paolo's call 2026-08-31 — perfect circle).**
  Four coplanar gold pads (2×8 mm each; outer force pair E3/E4, inner sense pair
  E1/E2) on the TOP face near the east rim, exposed through mask + epoxy exactly
  like the dock pads. The tongue was vestigial (it existed to poke through the
  old shell wall; the potted face IS in the water). Coplanar cell constant is
  higher and fringing-field dominated — irrelevant, K is calibrated empirically
  (never trusted from geometry). **Bubble caveat:** face pads can hold air after
  refills — place near the rim (pour turbulence sweeps them), and anomaly logic
  discards transient post-refill readings. Keep the L2 plane pulled back under
  the electrode zone (reduce capacitive shunt), and ≥8 mm from FDC pads.
- **Antenna sector**: module antenna end at the board edge, copper keep-out **≥5 mm on
  all four layers** (MDBT50Q datasheet §2.3 requires no ground "in each layer"), plus
  component/metal keep-out on the opposing face within the sector projection; air
  pocket preserved during potting (epoxy on the antenna ≈ half the range).

## On-board sensors

| Ref | Part | Package | Assembly |
|---|---|---|---|
| U3 | AS7341 (VDD on 1V8 from U10; GPIO → GND — *not* 3.6 V tolerant; INT/LDR NC) | OLGA-8 | JLC (LCSC C2655145) |
| U4 | FDC1004DGSR (SHLD1 = guard net; SHLD2 NC; CIN2 → FDC2 pad; CIN3/4 NC, no stubs) | VSSOP-10 | JLC (LCSC C2865994) |
| U5 | MS5837-02BA (VDD bound to always-on 3V3 — never GPIO-gated; power-up continuous) | LGA 3.3 mm, gel port | **hand-place**; nothing touches the gel; no-clean flux, no IPA wash near U5; mask port during dip |
| U6 | **DS18B20U+** (µSOP-8, 2026-09-05 — replaces the TO-92: no through-hole pins on the sensor face, JLC-placed) | µSOP-8 3×3 mm, project footprint `puck:DS18B20U_MSOP8` pads renumbered 1=GND/2=DQ/3=VDD to match the symbol | top face, on the axis; reads water temperature through the resin |
| U8 | LSM6DSO (0x6A: SDO/SA0 → GND, CS → VDDIO) | LGA-14 2.5×3 mm | JLC |
| U9 | IM69D130 PDM mic | PG-LLGA-5-1, bottom-port; sound inlet hole covered by an **IP68 acoustic vent membrane** (PTFE, adhesive) — passes sound, blocks water. SELECT → GND (mono). C11 100 nF + C17 1 µF at VDD. Mask during dip. | JLC |
| D1–D3 | white / 850 nm / 365 nm SMD LEDs | 3528/3535 | JLC — verify true 365 nm at BOM time |
| D7 | 275 nm UVC LED — **DNP, populate at v2** (footprints free now) | 3535-class (stock Cree-XP 3.45×3.45 mm land pattern; exact emitter chosen at v2) | DNP — hand-place at v2 |
| PD1 | GUVC-T21GH UVC photodiode — **DNP, populate at v2**. TO-5 metal can, 3 leads (Vcc/Vout/GND), **integrated transimpedance amp**, VCC 1.8–5.5 V, Vout = 0.355 V per mW/cm² → straight into AIN7. Datasheet on file (`docs/datasheets/guvc-t21gh.pdf`) | TO-5-3 THT | DNP — hand-place at v2; verify lead-vs-tab numbering against the can |

Optical zone: U3 + D1–D3 clustered top side; clear epoxy window over the cluster;
850 nm at ~90° to U3's view for scatter turbidity. **UVC organics channel (v2,
DNP):** D7 + PD1 + R25 grouped with the optical block — populate later; needs a
10–20 mm folded optical path at layout (fold the D7→PD1 line so absorbance at
275 nm gets enough water in the way). Note: the MS5837-02BA01 metal lid
is a *floating electrode* in the sample water — the calibration protocol includes an
EC-vs-U5 coupling check; don't casually swap to the grounded-lid variant.

## EC front end

Bipolar AC excitation, two-resistor auto-range, differential sense, gold pads are the
cell. Calibrate K vs 1413 µS/cm. ENIG fine for POC lifetime. Post-review circuit
(review C3/C4), upgraded to a **4-electrode (4-wire) cell** at the review follow-up:

- **Topology (4-wire):** E3/E4 are the **outer FORCE electrodes** — EC_DRV
  (P0.22/P0.23) drives through R3/R4 and the C1/C2 coupling caps into E3, returns
  via E4. E1/E2 are the **inner SENSE electrodes**, read differentially on
  EC_SENSE_A/B (P0.04/AIN2, P0.05/AIN3). The sense pair carries no current, so
  electrode fouling / double-layer impedance on the sense pads drops out of the
  measurement — only the force pair polarizes. EC_A/EC_B (AIN0/AIN1) stay on the
  force-pair nodes: they monitor the drive (and implement the Ron-elimination
  trick below). **2-electrode mode remains the firmware fallback** — same board,
  drive + sense on the force pair alone (that's exactly the pre-upgrade circuit);
  ship firmware brings up 2-electrode first, 4-wire is the accuracy upgrade.
  **R26/R27 (1 MΩ, on the sheet)** bias the sense nodes from the C16 mid-rail
  tap (same rule as C3 — SAADC inputs must never float; same 1 MΩ BOM line as
  R20–R24).

- **Coupling: C1/C2 4.7 µF X7R 0805** per leg (100 nF differentiated the excitation —
  the 1 kΩ range had no settled window). The electrode double-layer capacitance
  (~1.6 µF series) dominates at this scale, so residual low-range droop (~4.5 %) is
  chemistry-dependent → edge-synced sampling + per-range calibration against the KCl
  standards is **mandatory**; > 4.7 µF buys nothing.
- **Mid-rail bias network** (SAADC inputs must never float): R20/R21 1 MΩ divider
  VDD→GND with C16 100 nF at the tap, plus R22/R23 1 MΩ from the tap to *each*
  electrode/AIN node. Both electrodes bias to the same potential → zero net DC across
  the cell (electrolysis rule preserved). ~1.65 µA standing drain; ~1 % deterministic
  loading on the 100 kΩ range, calibrates out. Firmware: CH[n].CONFIG RESP/RESN =
  **Bypass** (never the internal ladder — unspecified resistance, unusable under
  rule 2).
- **Timing/acquisition policy** (review M9–M11): TACQ = **10 µs** (default 3 µs is
  rated to 10 kΩ source; the high range presents up to 100 kΩ). Drive pins configured
  **high-drive (H0H1)** (standard-drive Ron 100–400 Ω is a 20–40 % error on the 1 kΩ
  range; H0H1 → ~3–7 %, absorbed by KCl calibration). Idle range pin →
  `nrf_gpio_cfg_default()` (buffer disconnected — a driven-low idle pin makes a
  100k:1k divider and garbages the high range); both pins disconnected between bursts.
  Edge-synchronous sampling (GPIOTE toggle → PPI → TIMER fixed delay → SAADC SAMPLE).
  Per-range drive frequency: low range 5–10 kHz, high range ~1 kHz (the old
  ≤10 kHz pad ceiling is gone — EC drive now lives on full-drive P0.22/P0.23;
  frequencies stay a per-range calibration choice, not a pad limit). Two-pass gain
  (coarse at 1/6, re-acquire at max non-clipping). Discard ~1 s of startup cycles
  (cap charging). Optional zero-cost upgrade: sample the driving pad's own voltage
  (drive pins are AIN-capable) to eliminate Ron dependence entirely.
- **Every acquisition stores** TACQ / gain / reference / resolution / drive frequency /
  active range / drive strength / idle-pin state with the raw counts (rule 1).

## FDC1004 sense channel

- Single-ended **CIN1** with CAPDAC enabled; **SHLD1 driven guard** (review M6): void
  the L2 GND plane under the 10 mm pad, pour SHLD1-connected copper there extending
  ~2–3 mm beyond the pad edge, SHLD1 guard traces flanking the CIN1 run. A GND
  reference behind the pad would be ~18.5 pF of drifting parasitic against a ±15 pF
  full scale. SHLD2 = NC; **CIN2 → FDC2 pad** (below); CIN3/CIN4 = NC, no stubs
  (no DAP — VSSOP-10 has none). Shield load ≈ 4 pF ≪ 400 pF max. GND stays
  *around* (not under) the pad and mandatory around the I2C pins. Log the CAPDAC
  setting with every reading.
- **FDC2 — second capacitive pad (CIN2), review follow-up:** a second 10 mm
  sense pad at a **different board radius** than FDC1 → two points on the level
  gradient = redundant fill/level estimate and a sanity cross-check on FDC1
  drift. Same guard treatment (the SHLD1 pour behind it — one shield serves both
  CINs since the FDC1004 muxes channels against a common shield); single-ended
  CIN2 with its own CAPDAC value, logged like CIN1.

## Placement plan (circle, both sides)

- **TOP (sensor face):** U3+LEDs optical cluster (+U10 LDO; UVC v2 footprints
  D7/PD1/R25 adjacent, folded-path aperture reserved), U5 (port up), U4 + FDC1/FDC2
  sense pads at two radii, U6+R11 thermal pair, U8, U9 (inlet hole), EC face pads (4, near E rim), boost block.
- **BOTTOM (base face):** U1 module (antenna at edge sector + keep-out), U7 charger, SWD pads, TP1–TP20,
  4-pad dock constellation (GND/D−/D+/5V row) + dual keying magnets. **BT1 LiPo is OFF-BOARD** (area consequence): the
  pouch stacks UNDER the board inside the pot on its J1 leads, silicone-wrapped —
  puck gets ~4 mm thicker, board face frees ~600 mm². Keep the pouch + its foil
  clear of the NFC aperture and antenna sector projections.
- **Charging on the potted device:** magnetic charge pads (bottom face, masked during
  dip like the EC pads) + potted ring magnet. the dock carries charge AND full USB (DFU/UF2/serial) on both units — zero connectors anywhere.

### Layout rules (from the design review — items 16–18)

1. **BLE antenna:** keep-out ≥5 mm on **all four layers** + opposing-face component
   keep-out in the sector projection; boost hot loop diametrically opposite; SW-node
   copper minimal, cap returns via immediate L2 vias, shielded inductor; USB-C shell
   out of the sector. Optional and free: email the layout to service@raytac.com for
   the datasheet-offered pre-fab RF review (valuable under the 2-spin ceiling).
2. **NFC coil: off-board (2026-09-04), so no aperture on the board.** If a PCB spiral
   is ever revisited: copper keep-out on all 4 layers under the spiral +1 mm; ≥3–5 mm from every conductive neighbor (ring magnet OD, LiPo foil,
   module shield can, USB-C shell, charge pads); ≥5 mm from the BLE antenna sector.
   NFC1/NFC2 as a short differential pair with matched NP0 caps, values computed from
   the drawn spiral (likely 60–140 pF/pin), final tuning with magnet + battery
   installed, after the epoxy dip. Even at Ø46 the etched spiral is the tightest squeeze on the board — a smaller
   spiral (reduced range: tap must be precise) is acceptable; if it still won't fit:
   ferrite-backed flex antenna over the battery, or **drop NFC** (tap-to-pair is convenience, not a requirement).
   Check nRF52840 §6.14.11 (strong-field return current) at schematic review.
3. **Placement hygiene:** mic opposite the EC face pads (rail-to-rail MHz PDM clock vs
   the 100 kΩ differential EC nets; firmware also stops PDM during EC bursts);
   IMU/AS7341/mic off the heater pour — only the DS18B20 shares R11's thermal island
   (IMU zero-g drifts ±0.2 mg/°C: warm-up looks like tilt; gate tilt-wake reads away
   from heat pulses). R11 rating reconciled: **100 Ω 1 W 2512** (0.25 W actual
   dissipation) — spec and LIBRARIES.md now agree. Generous copper pour at U7
   (MCP73831 ~0.43 W at charge start; thermal regulation throttles under epoxy —
   accepted; consider RPROG 10 k / 100 mA for the potted unit).

## Bootloader + commissioning (before the shell is sealed)

Review items 12–15 — each of these is a brick-or-silent-failure trap:

1. **Custom bootloader build only — never a prebuilt hex.** The Adafruit
   nRF52 bootloader's top-level Makefile defines `CONFIG_NFCT_PINS_AS_GPIOS` for
   every board unless the board's `board.mk` sets **`USE_NFCT = yes`** (board.h edits
   do nothing — the flag comes from the Makefile). Even Adafruit's official prebuilt
   Raytac hex one-way burns UICR.NFCPINS on first boot: NFC dead, field-protection
   clamp gone, recoverable only via UICR erase over SWD — impossible after potting.
   Our board.mk sets `USE_NFCT = yes`. The Arduino core is safe; never add the flag
   to the puck variant. **Gate:** after bootloader flash + first boot,
   `nrfjprog --memrd 0x1000120C` must read `0xFFFFFFFF` (pre-dip checklist).
   Recovery pre-potting: NVMC ERASEUICR (not full eraseall) + re-flash bootloader.
2. **board.h:** BUTTON_DFU / BUTTON_FRESET on two spare, otherwise-unconnected GPIOs,
   each on a test point (tweezer-ground to force DFU pre-potting). **Blacklist as
   button pins:** IMU_INT (push-pull, can be driven at power-up), PDM pins, and any
   externally-driven/pulled net. One small LED + resistor on a VDD-side GPIO as
   LED_PRIMARY (D1–D3 are on the boost rail, which is down during DFU — invisible to
   the bootloader; DNP the LED on the potted unit if desired). Build with
   `CONFIG_GPIO_AS_PINRESET` → UICR PSELRESET on P0.18; keep RESET in the SWD pad set.
3. **UICR REGOUT0 = 3V3** at the one-time SWD flash (`nrfjprog --memwr 0x10001304
   --val 5` + pin reset), variant init guard, and the "rail measures 3.3 V"
   commissioning gate — details in the power section. Re-check after any eraseall.
   Decide 3V3 vs 3V0 together with the battery-floor policy.
4. **Puck variant: `USE_LFRC`** (no LF crystal on the module); base the bootloader on
   the **nice!nano** build (same module, no LF crystal, runs LFRC) — not the XIAO
   build. Never set DCDCEN0 (no LC on DCCH).
5. **Extended DFU gate:** before the dip, verify double-tap-reset DFU **and**
   app-initiated DFU (GPREGRET + soft reset / BLE OTA) — after potting,
   app-initiated OTA is the only entry path.

## Epoxy dip (commissioning gates first)

1. Sensors validated, EC calibrated, REGOUT0 + NFCPINS UICR gates passed, **BLE DFU
   round-trip proven incl. app-initiated OTA** (only reflash path after potting; SWD
   pads die under epoxy).
2. Mask: MS5837 port, EC face pads, mic inlet, dock pad constellation. (No tongue — outline is a perfect Ø46 circle.) Preserve antenna
   air pocket. Battery in soft silicone, never hard epoxy.
3. Clear epoxy over optical zone; thin coats; low exotherm; thermocouple first attempt.
4. Build 2: one naked dev unit forever, one potted demo unit.

## Full parts list (spin 1)

U1 MDBT50Q-1MV2 · U2 TPS61023 (SOT-563) · U3 AS7341 · U4 FDC1004 · U5 MS5837-02BA ·
U6 DS18B20 TO-92 · U7 MCP73831-2 · U8 LSM6DSO · U9 IM69D130 PDM mic ·
U10 XC6206P182MR (SOT-23, 1.8 V → AS7341 only) · BT1 protected LiPo 400–500 mAh ·
J1 JST-PH · D1–D3 SMD LEDs ·
D5 SS34 (**DNP** — not needed w/ TPS61023) · Q1–Q3, Q4, Q5 AO3400A (one BOM line) ·
L1 1 µH ≥2 A power inductor · C1,C2 4.7 µF X7R 0805 (EC coupling) · C3 100 µF 1210 ·
C5,C6 22 µF 16 V 0805 · C7–C10 100 nF decouplers (U3,U4,U5,U8) + C11 100 nF (U9) ·
C14,C15 1 µF (U10 in/out) · C16 100 nF (EC bias tap) · C17 1 µF (U9 bulk) ·
R1,R2,R14 4.7 k · R3 1 k · R4,R8–R10,R12 100 k · R5–R7 LED series (5 V rail ≤10 mA:
220/360/150 Ω) · R11 100 Ω 1 W 2512 · R13 220 Ω (piezo series) · R15 750 k · R16 100 k
(TPS61023 FB → 5.06 V) · R17 4.7 k (charge prog) · R29,R30 27 Ω (dock D± series) · U11 USBLC6-2SC6 ESD ·
R20–R24,R26,R27 1 MΩ (EC bias ×4 + piezo bleed + R26/R27 4-wire sense-pair bias
legs) · R25 series R for D7 (**DNP** — value at v2) · D8+R31 1 k status LED (0603 basic, P0.12) ·
D9 Schottky SOD-123 (ring supply drop) · D10–D21 XL-1010RGBC-WS2812B ring (12×, 2026-09-01) (LCSC C5349953,
extended, JLC-placed; alt SK6805-EC15 C2890035 at order time) · C18–C23 100 nF ring
decouplers · R32 220 Ω ring data series · C12,C13 NFC tuning (values
at layout) · NFC PCB coil (copper feature) · E1,E2 inner sense electrodes +
E3,E4 outer force electrodes (4-wire EC, all 2×8 mm gold) · CP1–CP4 dock pads (Ø2.0 mm ENIG, GND/D−/D+/5V @2.54 mm) · D6 SS14 · M1,M2 keying
magnets Ø5×2 N52, opposite polarities out, potted ≤0.8 mm deep · TP19,TP20 UART ·
FDC1 + FDC2 sense pads (copper features, two radii: Ø7.9 disc + Ø9.2–12.0 ring, concentric, 2026-09-05) · ~~D7 UVC LED / PD1 UVC
photodiode~~ (cut from spin 1, 2026-09-01) · PZ1 piezo (2 SMD wire pads) ·
TP1–TP18 (incl. 5V, BOOST_EN, VBUS) + SWD pads. **H1–H3 M2 mounting holes REMOVED
(Paolo's call 2026-08-31)** — board area + inner-layer routing freedom; the board is
retained by the shell instead: **shell design must provide a ledge/boss ring the
PCB seats on, plus preload** (foam pad or the O-ring lid pressing the stack) so the
dock pads keep contact pressure and the puck survives tilt/shake without rattling.

## JLCPCB order

**Finish for looks (the board is visible through clear resin): MATTE BLACK solder
mask + ENIG** — gold pads/electrodes/traces-glints on black is the product's
visual identity. Minimal silkscreen: hide reference designators on the outer
layers at plot time (keep them in fab notes); only deliberate marks (logo/name,
pin-1 dots where assembly needs them). Check at order: black 4-layer lead-time
adder at JLC.

4-layer, Ø46 circle, ENIG, black mask, **assembly BOTH faces** (all SMD incl. U8 LGA
and U4 VSSOP on the bottom), qty 5 / assemble 2. Hand-place: U1 module, U5, U6, J1, piezo wires, battery. Pre-order checks: ERC/DRC, Gerber render, JLC rotation review
part-by-part, **1:1 paper check with the MDBT50Q land pattern** (redo — the old check
was against the E73).

## Firmware deltas

- Custom board variant in the Adafruit nRF52 core (pin map above); the XIAO stays the
  bench mule — same drivers, recompiled. platformio.ini gains an **`mdbt50q_puck`**
  env. Variant: `USE_LFRC`, REGOUT0 guard, never `CONFIG_NFCT_PINS_AS_GPIOS`, never
  DCDCEN0.
- One-time bootloader flash over SWD before anything else (custom build, `USE_NFCT =
  yes`, nice!nano base — see commissioning section).
- **TX policy (review item 19):** default 0 dBm, cap +4 dBm unless the radio-vs-load
  interlock guarantees quiescent VDD loads during TX; System OFF budget < 1 mA with
  the PDM clock stopped.
- **EC driver (review item 20):** TACQ 10 µs via nrfx (also needed for true
  differential — `analogRead()` is single-ended-only; bench mule uses
  `analogSampleTime(10)` today in `ec_bringup.cpp`); drive pins H0H1; idle range pin
  `nrf_gpio_cfg_default()` in the range-switch routine, both pins disconnected between
  bursts; edge-synced sampling (GPIOTE→PPI→TIMER→SAMPLE); per-range drive frequency
  (low 5–10 kHz, high ~1 kHz — no pad ceiling anymore, EC drive is on full-drive
  P0.22/P0.23); two-pass gain; discard ~1 s startup; log every
  acquisition setting with the raw counts (rule 1). **4-wire mode** (accuracy
  upgrade after 2-electrode bring-up): drive the force pair, sample EC_SENSE_A/B
  (AIN2/AIN3) differentially for the cell voltage while AIN0/AIN1 watch the force
  nodes; store both pairs' raw counts + which topology produced them (rule 1).
- **Power/telemetry (review item 21):** log VBAT (VDDHDIV5) + VDD with every sample;
  battery-empty ≈ 3.5–3.6 V VDDH; flag FDC/DS18B20 samples with VDD < 3.0 V;
  bench-measure actual REG0 output at commissioning. FDC1004: single-ended CIN1 +
  CAPDAC, log CAPDAC. PDM: log PDMCLKCTRL/RATIO/GAIN per capture, discard first
  ~10 ms (mic Ton). Sleep during charging so MCP73831 termination sees true battery
  current.
- Boost sequencing unchanged: EN high → settle → burst → EN low.
- DFU gate before dip (incl. app-initiated OTA — see commissioning section).
