# Carrier Board Design Review

**Date:** 2026-08-31
**Reviewed design:** `hardware/carrier-board-spec.md`
**Method:** 6 subsystem reviewers (module-pins, power, i2c-bus, sensors, ec-adc,
rf-nfc-system) working against the downloaded datasheets in `docs/datasheets/`
(13 PDFs, all verified against expected parts). Every critical/major finding was
then adversarially verified by an independent agent against the same datasheets
and the repo state. Result: **29 confirmed** (7 critical / 22 major raw; **5
critical / 15 major after dedup**), **5 refuted**, 19 minors, 0 unverified.

**Part-swap context (decided after the review ran, applied throughout):**
- **U1 is the Raytac MDBT50Q-1MV2** (E73 retired 2026-08-30). All E73 pin-gap
  findings are **MOOT** — the MDBT50Q exposes every spec pin (datasheet §2.5,
  confirmed in LIBRARIES.md). Kept below for the record. P0.28/P0.29 are
  standard-drive ≤10 kHz low-frequency pads; an EC-drive pin-move is already
  planned.
- **Boost MT3608 → TPS61023** (true load disconnect) — resolves the
  always-live-rail/FB-bleed finding.
- **IMU LIS2DW12 → LSM6DSO**, **mic MP34DT06J → IM69D130** — findings against
  the old parts are marked; equivalent checks carry over to the new parts.

---

## 1. Confirmed findings

### Critical

#### C1. AS7341 on the 3.3 V rail exceeds its 2.2 V absolute maximum — part will be destroyed
*Found independently by power, i2c-bus, and sensors reviewers. Verifier confidence: high (all three).*
- **Component:** U3 AS7341 (bare OLGA-8, JLC-assembled)
- **Problem:** The board has only two rails (module 3.3 V VDD, boost 5 V). The
  AS7341 is a 1.8 V-core part: operating VDD 1.7–2.0 V, **absolute max 2.2 V**.
  At 3.3 V it is damaged or destroyed. Every AS7341 breakout carries an onboard
  1.8 V LDO for exactly this reason; mounting the bare chip loses that.
- **Evidence:** as7341.pdf DS000504 v3-00, Fig. 5 Abs Max: "VDD/VGND −0.3 …
  2.2 V"; Fig. 6: VDD min 1.7 / typ 1.8 / max 2.0 V. Digital pins (SCL/SDA/INT)
  and LDR are separately rated to a fixed 3.6 V, VIH min 1.26 V — so the shared
  3.3 V I2C bus is fine; **only VDD needs 1.8 V**.
- **Fix:** Add U10 = XC6206P182MR (1.8 V, SOT-23, hand-solderable, ~1 µA Iq,
  same family as the project's LDO fallback), input from 3V3, output feeding
  **only** U3 VDD. ~1 µF ceramic on LDO in and out (100 nF alone is marginal
  for XC6206 stability); keep C7 100 nF at U3 VDD on the 1V8 net. No level
  shifter. If INT is ever routed, its pull-up may go to 3.3 V (≤3.6 V abs max).
  Never tie AS7341 **GPIO** to 3.3 V — it is *not* 3.6 V tolerant (1.8 V core).
  Update spec power section + parts list + STATUS.md.

#### C2. UICR REGOUT0 defaults to 1.8 V — the entire "3V3" rail is 1.8 V until programmed
*Found by module-pins, power, and i2c-bus reviewers (rated critical by power). Verifier confidence: high.*
- **Component:** U1 nRF52840 REG0 / commissioning flow
- **Problem:** With LiPo→VDDH (high-voltage mode, "no LDO"), the VDD pin is
  REG0's *output*, set by UICR REGOUT0 — reset value = **1.8 V**. The module
  ships blank, so first power-up runs the whole sensor rail, all GPIO high
  levels, and I2C at 1.8 V: FDC1004 and DS18B20 (both 3.0 V min) dead, 2N7002
  gates (VGSth up to 2.5 V) may never turn on. The board "boots" (BLE works)
  and silently fails. Any later `--eraseall` wipes UICR and resurrects the trap
  — fatal if it happens after potting.
- **Evidence:** nrf52840.pdf §4.5.1.8 (REGOUT0 reset 0xFFFFFFFF, DEFAULT =
  1.8 V; 5 = 3.3 V); §5.3.1.2 (GPIO high level = REGOUT0 level); §5.3.1.3.
  fdc1004.pdf §5.3 (3.0–3.6 V); ds18b20.pdf (3.0–5.5 V).
- **Fix (three-layered):** (1) Commissioning step in the one-time SWD flash:
  `nrfjprog --memwr 0x10001304 --val 5` + pin reset (writes into the all-ones
  default without erase); then **measure 3.3 V on the 3V3 pad** before any
  sensor bring-up. Do not rely on the bootloader — its REGOUT0 fixup is
  variant-dependent and only runs when powered via VDDH; verify the chosen
  build's source. (2) Belt-and-suspenders guard in the puck variant init:
  if REGOUT0 is default → NVMC write VOUT=3V3 → `NVIC_SystemReset()` (Nordic's
  standard pattern) — protects against post-potting chip erase + DFU reflash.
  (3) Add "REGOUT0=3V3 verified (rail measures 3.3 V)" to STATUS.md
  commissioning gates next to the DFU round-trip; re-check after any eraseall.

#### C3. EC SAADC inputs float with no DC bias path — common mode drifts out of the legal window
*Found by ec-adc reviewer. Verifier confidence: high.*
- **Component:** EC front end — C1/C2 100 nF coupling, EC_A/EC_B (AIN0/AIN1)
- **Problem:** The differential SAADC taps the electrode side of the coupling
  caps; every DC path to those nodes goes through a capacitor. Common-mode
  voltage is set only by leakage/charge injection, drifts to a rail, and the
  ±1.65 V AC swing then drives one AIN past VSS/VDD — ESD clamps conduct,
  readings are garbage, and rectified clamp current flows as **net DC through
  the water**, violating the very rule the caps enforce.
- **Evidence:** nrf52840.pdf §6.23.2: "Inputs AIN0 through AIN7 cannot exceed
  VDD or be lower than VSS"; §6.23.10.1 (CSAMPLE 2.5 pF, RINPUT >1 MΩ — nothing
  defines the node's DC level). Spec lines 50, 91–93: caps in series both legs,
  no bias network in the parts list.
- **Fix:** Mid-rail bias network: 2× **1 MΩ** divider VDD→GND with 100 nF at
  the tap, plus 1 MΩ from *each* electrode/AIN node to the tap. Both electrodes
  bias to the same potential → zero net DC across the cell (electrolysis rule
  preserved). ~1.65 µA standing drain; ~1 % deterministic loading on the 100 kΩ
  range, calibrates out against the KCl standards. +5 parts, all 0603/0805.
  Firmware: set CH[n].CONFIG RESP/RESN = **Bypass** (don't parallel the
  internal ladder — its resistance is unspecified, unusable under rule 2).

#### C4. 100 nF coupling caps differentiate the excitation — no settled window on the 1 kΩ range
*Found by ec-adc reviewer. Verifier confidence: high (independently recomputed).*
- **Component:** EC front end — C1/C2 = 100 nF, R3 = 1 kΩ range
- **Problem:** Two 100 nF in series = 50 nF effective. At 12.88 mS/cm
  (Rcell ≈ 78 Ω, K≈1) τ ≈ 60 µs: at 1 kHz the signal decays to ~0.02 % before
  sampling (dead); at 10 kHz it droops ~56–58 % within one half-cycle — the
  result depends entirely on sampling phase. Same failure at 1413 µS/cm. Only
  the 100 kΩ range survives as specced.
- **Evidence:** Computed from spec values (lines 50–51, 91–93, 116–117);
  nrf52840.pdf Table 95 + §6.23.10.1 for the sampling-window requirement.
  Verifier independently reproduced the math.
- **Fix:** C1/C2 → **4.7 µF X7R 0805** (limits DC-bias derating). Drive the low
  range at 5–10 kHz, high range at ~1 kHz. Sample **edge-synchronously**
  (GPIOTE toggle → PPI → TIMER fixed delay → SAADC SAMPLE) so residual droop is
  a calibrated constant. Discard ~1 s of startup cycles (cap charging).
  Verifier correction: the gold pads' electrode double-layer capacitance
  (~1.6 µF series) dominates once coupling caps reach µF scale — real low-range
  droop ≈ 4.5 % and chemistry-dependent, so edge-sync + per-range calibration
  against the 1413 µS/cm standard is **mandatory**, and >4.7 µF buys nothing.

#### C5. U1 in the schematic is still the retired E73 — swap to MDBT50Q-1MV2 before any wiring
*Found by rf-nfc (critical), i2c-bus, and ec-adc reviewers. Verifier confidence: high. **Decision MOOT — migration action remains.***
- **Component:** U1 in `puck-carrier.kicad_sch` / `.kicad_pcb`
- **Problem:** The module decision is settled (spec + LIBRARIES.md both say
  MDBT50Q-1MV2; E73 retired 2026-08-30; symbol/footprint/STEP authored and
  61-pad verified; datasheet on file). But the live design files still
  instantiate U1 as `puck-extra:E73-2G4M08S1C` (plus a "BRAIN — E73" schematic
  note), and `scripts/gen_schematic.py` still emits the E73 block. Wiring today
  targets the wrong, retired module whose castellations lack six spec pins.
- **Evidence:** mdbt50q-1mv2.pdf §2.5 confirms every spec pin exposed (P0.27=16,
  P0.14=36, P0.16=38, P0.19=42, P0.21=43, P0.25=49, NFC 52/54, VDDH=30, USB
  32/34/35) — **no remap needed**. LIBRARIES.md line 35 (U1 = MDBT50Q), line 36
  (E73 RETIRED).
- **Fix:** Swap U1 symbol/footprint to `puck-extra:MDBT50Q-1MV2` /
  `puck:MDBT50Q-1MV2` (update gen_schematic.py, regenerate), fix the BRAIN
  note, run Update PCB from Schematic, redo the 1:1 paper footprint check with
  the MDBT50Q land pattern before ordering. Honor the §2.6 caveat: P0.28/P0.29
  are ≤10 kHz low-frequency pads — fine while EC excitation stays ≤10 kHz (a
  pin-move is already planned). Clean stale strings: LIBRARIES.md line 8 "bare
  E73", spec line 131 `e73_puck` env, STATUS.md.

### Major

#### M1. REG0 dropout + −10 % tolerance vs the FDC1004/DS18B20 3.0 V floor
*Found by power and i2c-bus (+ module-pins minor). Confidence: high.*
- **Problem:** REG0 needs VDDH ≥ VDD + 0.3 V, so 3.3 V holds only above
  VBAT ≈ 3.6 V; below, VDD tracks VBAT − 0.3 V. Worse, VDDOUT error is −10/+5 %:
  a 3.3 V setting can legally sit at **2.97 V — below FDC1004's 3.0 V minimum
  at full battery**. (Verifier: "most of the discharge curve" was overstated —
  exposure is roughly the last 10–30 % of capacity, but the −10 % case is
  zero-margin everywhere.)
- **Evidence:** nrf52840.pdf §5.3.8.2 (VREG0,DROP 0.3 V; VDDOUT,ERR −10/+5 %);
  fdc1004.pdf §5.3; ds18b20.pdf. MS5837/LIS2DW12/mic unaffected (1.5–1.6 V min).
- **Fix (option 2, sharpened — verifier rejected the split-rail LDO option: it
  breaks I2C VIH compatibility, product-answer complexity):** (1) REGOUT0=3.3 V;
  define battery-empty at VDDH ≈ 3.5–3.6 V via the SAADC **VDDHDIV5** internal
  channel (free, no divider). (2) Bench-measure the actual REG0 output at
  commissioning (n=1 static offset; bump REGOUT0 if <3.05 V). (3) Log VDD and
  VDDH/5 with every FDC1004/DS18B20 acquisition; flag samples with VDD <3.0 V
  as out-of-spec rather than discarding (rule 1). (4) Record floor + threshold
  in spec + STATUS.md.

#### M2. REG0 external-current budget: 25 mA at TX ≤ +4 dBm, only 5 mA above, 1 mA in System OFF
*Found by module-pins and power (+ i2c-bus minor). Confidence: high.*
- **Problem:** External draw = **sum of all GPIO currents + VDD pin current**
  (footnote 10). Worst-case concurrent sensor load ≈ 6.6 mA — breaches the 5 mA
  budget for TX > +4 dBm; add piezo (~15 mA via R13 220 Ω, also above the pin's
  drive rating) + EC drive (~3.3 mA) and everything-at-once grazes even 25 mA.
- **Evidence:** nrf52840.pdf §5.3.8.2 pp. 80–81 (IEXT,OFF/LOW/HIGH + footnote
  10); sensor currents verified in each datasheet. MDBT50Q supports +8 dBm.
- **Fix:** (1) Firmware policy in the spec: default TX 0 dBm, hard cap +4 dBm
  *unless* a radio-vs-load interlock guarantees all VDD loads quiescent during
  TX (store-and-forward already decouples sampling from sync — nearly free);
  note DC/DC does **not** raise IEXT limits. (2) Move the piezo off the GPIO:
  low-side FET switch (gate via ~1 k, piezo from 5 V/VBAT via series R, bleed
  resistor across it) — removes the largest GPIO current and the drive-rating
  violation. (3) Written System OFF budget < 1 mA before layout — critically,
  the PDM mic clock must be stopped in System OFF (650 µA running vs 5 µA off).
  Optional: one P-FET high-side switch gating the whole sensor cluster.

#### M3. No 32.768 kHz crystal on the module — a XIAO-style USE_LFXO build hangs at boot
*Found by module-pins. Confidence: high (verifier confirmed the same trap applies to the MDBT50Q).*
- **Problem:** The MDBT50Q-1MV2 has no LF crystal on-module (XL1/XL2 =
  user-supplied). The XIAO bench mule's variant hard-codes `USE_LFXO`; a puck
  variant copied from it makes the SoftDevice wait forever for a crystal that
  isn't there — board appears dead on first bring-up. No LF-clock config exists
  anywhere in `firmware/` today.
- **Evidence:** mdbt50q-1mv2.pdf §3/§8 (only 32 MHz crystal internal; "need to
  add external 32.768khz" or use internal RC); nrf52840.pdf §5.4; installed
  Seeed variant.h line 9 `#define USE_LFXO`.
- **Fix:** (1) Puck variant.h: `USE_LFRC`, not `USE_LFXO` (core then configures
  NRF_CLOCK_LF_SRC_RC with calibration — fine for a BLE peripheral); frees
  P0.00/P0.01 as spare GPIO. (2) Same for the bootloader: base it on the
  **nice!nano** build (same module, no LF crystal, runs LFRC) — not the XIAO
  build. (3) Document LFRC + bootloader caveat in the spec firmware deltas;
  rename the stale `e73_puck` env.

#### M4. Boost EN low does not disconnect the 5 V rail; 77 k FB divider bleeds ~47 µA forever — **RESOLVED by MT3608 → TPS61023 swap**
*Found by power. Confidence: high. Kept for the record.*
- **Problem (MT3608):** Async boost — permanent DC path VBAT→L1→D5→rail
  regardless of EN; rail sits at ~VBAT−0.2 V; R15/R16 (77.1 k) bleed ~47 µA
  24/7 ≈ 31–39 % of the 400 mAh cell per semester; heater/LED nets always live.
- **Resolution:** TPS61023 has true output load disconnect and its own FB
  arrangement. **Carry-over checks for the new part:** verify EN logic level
  from 3.3 V (and 1.8 V pre-UICR) GPIO, size the FB divider (if external) for
  low standing drain, and keep the hot-loop placement rule (M14). Re-verify the
  5 V setpoint and inductor selection against the TPS61023 datasheet; update
  spec + STATUS.md.

#### M5. 2N7002 gate drive is marginal at 3.3 V — defeats the constant-LED-brightness rationale
*Found by power. Confidence: high.*
- **Problem:** 2N7002 VGSth up to 2.5 V; RDSon spec'd only at VGS ≥ 4.5 V. At
  3.3 V (worse when the rail sags to ~2.7 V) a worst-case part is tens of ohms
  against 150–360 Ω LED resistors → LED current becomes battery-dependent —
  exactly what the boost was kept to prevent. Typical parts mask this on the
  bench.
- **Evidence:** 2n7002.pdf (Nexperia): VGSth 1/2/2.5 V; RDSon 5.3 Ω max only at
  4.5 V. ao3400.pdf: VGS(th) 0.65–1.45 V, ≤48 mΩ at VGS 2.5 V.
- **Fix:** Q1–Q3 → **AO3400A** (drop-in SOT-23, same pinout, already Q4 in the
  BOM — deletes a line item). Confirm gate pulldowns (100 k) on Q1–Q3 so LEDs
  stay off while GPIOs are Hi-Z during boot/DFU.

#### M6. FDC1004 SHLD1 active shield missing — and the plan puts the sense pad over the L2 GND plane
*Found by i2c-bus and rf-nfc. Confidence: high.*
- **Problem:** The spec never assigns SHLD1/SHLD2, and "defined reference
  behind the FDC pad" implies GND on L2. The FDC1004 measures CIN-to-GND: a
  10 mm pad over GND across ~0.21 mm prepreg is **~18.5 pF of fixed parasitic
  vs a ±15 pF full scale** — and TI's datasheet warns exactly this parasitic
  drifts with temperature/humidity/mechanics (a potted board cycling into
  chilled water is the textbook failure mode). CAPDAC recovers range but not
  drift.
- **Evidence:** fdc1004.pdf §6.3.1 (SHLDx driven to CIN potential "to eliminate
  the CINn parasitic capacitance to ground"), §6.3.2 (±15 pF FS, CAPDAC
  ~96 pF), §7.2.1/7.2.2 (TI liquid-level ref design: bottom layer = shield
  plane, not GND), §7.6.1/7.6.2 (GND far from channel traces, mandatory around
  I2C pins), max shield load 400 pF.
- **Fix:** Void the L2 GND plane under the pad; pour **SHLD1**-connected copper
  there, extending ~2–3 mm beyond the pad edge; SHLD1 guard traces flanking the
  CIN1 run (Fig. 7-3). SHLD2 = NC; CIN2–CIN4 = NC, no stubs. No DAP action —
  FDC1004DGSR (VSSOP-10) has none. Firmware: single-ended CIN1 with CAPDAC
  enabled (SHLD1 then tracks CIN1); log the CAPDAC setting with every reading.
  Shield load to L3 ≈ 4 pF — far under 400 pF. Add SHLD1 to the spec net list.

#### M7. nRF PDM default clock (1.032 MHz) is in the MP34DT06J's undefined region — **likely RESOLVED by mic swap to IM69D130 (verify)**
*Found by sensors. Confidence: high. Kept for the record.*
- **Problem (MP34DT06J):** Normal-mode clock range 1.2–3.25 MHz; the Adafruit
  PDM library default (1.032 MHz) sits in the undefined 0.23–1.2 MHz region —
  audio may be attenuated/noisy/dead, varying unit to unit (poison for rule 1).
- **Resolution/carry-over:** Verify the **IM69D130's** PDM clock range against
  its datasheet before trusting the library default; if any doubt, hard-code
  PDMCLKCTRL = 1280K + RATIO = Ratio80 (Nordic-documented pair, exactly 16 kHz
  PCM), applied after `PDM.begin()` or baked into the variant. Either way, log
  PDMCLKCTRL/RATIO/GAIN with every capture, and discard the first ~10 ms after
  start (mic Ton).

#### M8. IMU CS/SA0 ties missing from the spec — **superseded by IMU swap to LSM6DSO (requirement carries over)**
*Found by sensors (+ i2c-bus minor). Confidence: high.*
- **Problem (LIS2DW12):** I2C mode requires CS tied high; address 0x19 requires
  SA0 high. Internal pull-ups make a floating build work by luck — but the CS
  pull-up is software-disableable, and a floating mode pin in a potted puck
  next to a switcher is a latent SPI-glitch failure.
- **Carry-over:** The LSM6DSO has the same convention (CS high for I2C;
  SDO/SA0 selects address). At wiring: tie CS and SDO/SA0 to VDD_IO, record the
  resulting address in the spec pin map, and confirm no address clash on the
  bus (0x6A/0x6B for LSM6DSO — no conflict with 0x39/0x50/0x76). Also re-check
  the tilt-wake interrupt pin polarity/default for the bootloader-button
  blacklist (M15).

#### M9. Default 3 µs SAADC acquisition time is too short for the EC source impedance
*Found by ec-adc. Confidence: high.*
- **Problem:** The stock `analogRead()` uses TACQ = 3 µs, rated only to 10 kΩ
  source resistance; the high range presents up to ~100 kΩ (bounded by the
  drive resistor). High-range counts settle incompletely and read low, with an
  impedance-dependent (silently data-corrupting) error. The bench sketch
  `firmware/src/bench/ec_bringup.cpp` has this bug today.
- **Evidence:** nrf52840.pdf Table 95 (3 µs→10 k … 10 µs→100 k); installed core
  `wiring_analog_nRF52.c:33` defaults TACQ 3 µs.
- **Fix:** (1) Bench, now: `analogSampleTime(10)` in setup — one line; 10 µs
  covers the worst case on both ranges (source is *capped* at 100 kΩ by the
  drive resistor — the 40 µs/800 kΩ row buys nothing). (2) Carrier firmware:
  drive the SAADC via nrfx — required anyway because `analogRead()` is
  single-ended-only and the spec needs true differential — with per-range
  TACQ, and store TACQ/gain/reference/resolution/frequency/range with the raw
  counts (rule 1). Flag near-full-scale high-range deltas as below-range.

#### M10. GPIO output resistance (~200–400 Ω standard drive) is an unmodeled 20–40 % error on the 1 kΩ range
*Found by ec-adc. Confidence: high.*
- **Evidence:** nrf52840.pdf GPIO spec: standard drive Ron 100–400 Ω; high
  drive ~30–70 Ω.
- **Fix:** (1) Configure EC drive pins **high drive (H0H1)** → ~3–7 % mostly
  deterministic, absorbed by KCl calibration. (2) Log drive strength with raw
  counts. (3) Zero-cost upgrade: the drive pins are also AIN-capable — sample
  the driving pad's own voltage during each half-cycle and compute Rcell from
  measured Vpad, eliminating Ron/temperature dependence entirely. (4) Calibrate
  at all three standards; the 12.88 mS point exercises Ron hardest.

#### M11. Idle range pin must be truly disconnected, not driven low
*Found by ec-adc. Confidence: high.*
- **Problem:** Both range resistors share the drive node. EC_DRV_LO left as a
  driven-low output during 100 kΩ excitation makes a 100k:1k divider — only
  ~33 mV reaches the cell; high-range readings are garbage while still
  appearing to respond. The spec states no idle-pin policy; the naive
  both-pins-OUTPUT implementation fails exactly this way.
- **Fix:** In the EC driver's range-switch routine (single choke point): idle
  pin → `nrf_gpio_cfg_default()` (input, **buffer disconnected**, no pull) —
  not plain `pinMode(INPUT)`. Return *both* pins to cfg_default after each
  burst (also serves the no-DC rule). Record active/idle pin state with the
  acquisition (rule 1). Add one line to the spec. Validate the high range
  against dilute KCl to prove the policy.

#### M12. Bootloader can permanently burn UICR.NFCPINS to GPIO mode, silently killing NFC
*Found by rf-nfc. Confidence: high — verifier found it is WORSE than claimed.*
- **Problem:** The Adafruit_nRF52_Bootloader **top-level Makefile defines
  `CONFIG_NFCT_PINS_AS_GPIOS` by default for every board** unless board.mk sets
  `USE_NFCT = yes` (only 4 boards do; nice_nano, nrfmicro, and both
  raytac_mdbt50q boards do NOT). Even Adafruit's official prebuilt Raytac hex
  one-way burns NFCPINS on first boot: NFC dead, field-protection clamp gone
  (reader-field damage possible), recoverable only via UICR erase over SWD —
  impossible after potting.
- **Evidence:** nrf52840.pdf §4.5.1.6, §6.14.3 ("never leave the DISABLE
  state"); mechanism confirmed in the installed core's system_nrf52840.c;
  Makefile behavior confirmed by cloning the bootloader repo.
- **Fix:** (1) Custom bootloader board: add **`USE_NFCT = yes` in board.mk**
  (board.h edits do nothing — the flag is injected by the Makefile). (2)
  **Never flash a prebuilt hex** on this module. (3) Arduino core is safe;
  never add the flag to the puck variant. (4) Commissioning gate: after
  bootloader flash + first boot, `nrfjprog --memrd 0x1000120C` must read
  0xFFFFFFFF, in the pre-dip checklist. (5) Recovery pre-potting: NVMC
  ERASEUICR (not full eraseall) + re-flash bootloader.

#### M13. NFC coil environment unspecified — needs an all-4-layer copper void and conductive-neighbor clearances
*Found by rf-nfc. Confidence: high.*
- **Problem:** Any plane copper behind the spiral is a shorted turn; the board
  philosophy is solid GND on L2 everywhere. Both faces are hostile (module
  shield can, LiPo foil, USB-C shell, charge pads, nickel-plated ring magnet /
  FDC pad, optics, EC tongue), the spec never even picks a face, and fitting a
  ~20 mm aperture + ≥5 mm BLE clearance on a Ø50 mm board is a real geometry
  problem. No rework after potting.
- **Fix:** At placement, draw the coil aperture **first**: copper keep-out on
  all 4 layers under the spiral +1 mm; ≥3–5 mm from every conductive neighbor;
  ≥5 mm from the BLE antenna sector; NFC1/NFC2 as a short differential pair
  with matched caps. Amend the "solid ground" note so the void is a planned
  exception. If it won't fit: ferrite-backed flex NFC antenna over the battery,
  or **drop NFC** (tap-to-pair is convenience, not a requirement). Final cap
  tuning with magnet + battery installed, after the epoxy dip. Check §6.14.11
  (strong-field return current into supply) at schematic review. Related minor:
  the 300 pF tuning caps are a placeholder for a ~0.9 µH coil — compute from
  the drawn spiral (likely 60–140 pF/pin), matched NP0 values.

#### M14. BLE antenna keep-out written as "both layers" on a 4-layer board; boost hot loop unconstrained
*Found by rf-nfc (+ module-pins minor). Confidence: high.*
- **Problem:** As written, L2/L3 planes may flood under the antenna —
  MDBT50Q-1MV2 datasheet §2.3 requires no ground "in EACH LAYER" of the antenna
  zone. The boost hot loop (strongest broadband emitter, 1.2 MHz + light-load
  PFM spurs) has no placement constraint vs the antenna sector. (Boost part is
  changing to TPS61023 — the hot-loop rule stands.)
- **Fix:** Spec amendments: keep-out ≥5 mm on **all four layers** plus
  component/metal keep-out on the opposing face within the sector projection;
  qualify the "solid ground" line. Placement: boost hot loop diametrically
  opposite the antenna sector, SW node copper minimal, cap returns via
  immediate L2 vias, shielded inductor; USB-C shell out of the sector.
  Optional and free: email the layout to service@raytac.com — the datasheet
  offers pre-fab RF review (valuable under the 2-spin ceiling).

#### M15. Bootloader board.h needs BUTTON_DFU / BUTTON_FRESET / LED reserved — never on nets driven low at boot
*Found by rf-nfc. Confidence: high.*
- **Problem:** Every Adafruit bootloader board.h defines DFU/FRESET buttons
  (sampled at reset with pull-ups) and a status LED. A donor-board copy-paste
  that lands BUTTON_DFU on a net this design drives low bricks normal boot —
  concrete trap: the IMU INT pin is push-pull **forced to GND at power-up**
  (LIS2DW12 datasheet; re-check LSM6DSO, same convention likely). D1–D3 hang
  off the boost rail, which is down during DFU — no bootloader-visible LED.
- **Fix:** (1) Puck-specific board.h: BUTTON_1/BUTTON_2 on two spare,
  otherwise-unconnected GPIOs, each on a test point (tweezer-ground to force
  DFU pre-potting). (2) Spec blacklist: IMU_INT, PDM pins, and any
  externally-driven/pulled net as button pins. (3) One small LED + resistor on
  a VDD-side GPIO as LED_PRIMARY (DNP on the potted unit if desired). (4) Build
  with CONFIG_GPIO_AS_PINRESET → UICR PSELRESET on P0.18; keep RESET in the SWD
  pad set. (5) Extend the pre-dip DFU gate: verify double-tap-reset DFU **and**
  app-initiated DFU (GPREGRET + soft reset / BLE OTA) — after potting,
  app-initiated OTA is the only entry path.

---

## 2. Refuted findings (false alarms, on record)

1. **"Six spec GPIOs (incl. SCL) don't exist on the module's castellations"
   (module-pins, critical)** — Verified against the wrong module. U1 is the
   MDBT50Q-1MV2, which exposes all six (P0.27/14/16/19/21/25). MOOT.
2. **"Spec and library disagree on which module U1 is" (module-pins,
   critical)** — LIBRARIES.md already lists U1 = MDBT50Q (E73 explicitly
   RETIRED); symbol/footprint/datasheet all exist and are verified. The real
   residue — the schematic still instantiating the E73 — is captured as C5.
3. **"Module identity conflict — power pins/footprint incompatible" (power,
   major)** — Same refutation: mdbt50q-1mv2.pdf on file (VDD=28, VDDH=30);
   verified symbol matches. Battery→VDDH plan stands.
4. **"DS18B20 powered from the switched 5 V boost rail" (sensors, major)** —
   False premise: the spec scopes the 5 V rail to LEDs + heater only; U6 was
   always on VDD. Salvage: reword spec line 53 "pull-up to VDD" → "to 3V3" for
   clarity.
5. **"Spec pin map: six pins not exposed / module disagreement" (sensors,
   major)** — Duplicate of 1–2; quoted the retired-reference section of
   LIBRARIES.md as if current. Only cosmetic stale strings remain.

---

## 3. Minor + unverified findings (compact)

**Unverified: none.** Minors by subsystem:

**module-pins**
- REGOUT0=3.3 V drops regulation over much of the LiPo curve → consider
  REGOUT0=**3V0** (in regulation down to VDDH 3.3 V; all rail sensors OK at
  3.0 V, DS18B20 binding) — decide together with M1; recompute pull-up/gate
  margins at 3.0 V.
- **Pin map omits VBUS** — nRF USB does not enumerate without 5 V on the
  module's VBUS pad. Add pin-map row (USB-C VBUS after CC pull-downs → module
  VBUS pad + local decoupling). USB DFU on the dev unit depends on this.
- NFC works with default UICR but the firmware variant must never define
  CONFIG_NFCT_PINS_AS_GPIOS (superset of M12).
- Antenna keep-out "both layers" is leftover 2-layer wording (folded into M14);
  no routing under the module body on any layer per module manual.
- DCCH pad: leave unconnected, and firmware must never set DCDCEN0 (no LC
  fitted — enabling it soft-bricks the board incl. debug access).

**power**
- MCP73831 has no power path: system load distorts charge termination →
  firmware sleeps (radio off, sensors idle) whenever charger power detected;
  note in STATUS.md.
- MCP73831 dissipates ~0.43 W at charge start; thermal regulation throttles the
  213 mA claim, worse under epoxy → accept; generous copper pour; consider
  RPROG 10 k (100 mA) for the potted unit; add the SS14 datasheet.
- 22 µF boost caps in 0603 derate 50–70 % at 5 V bias → 0805/1206, 16–25 V,
  check DC-bias curve at BOM time (re-select for TPS61023 anyway).

**i2c-bus**
- LIS2DW12 SA0/CS/NC ties (merged into M8; carries to LSM6DSO).
- AS7341 GPIO/INT/LDR terminations unspecified — GPIO is **not** 3.6 V
  tolerant: GPIO → GND (never 3.3 V); INT → NC or pull-up per C1; LDR → NC.
- REG0 5 mA-during-TX budget (duplicate of M2).

**sensors**
- Optional: AS7341's built-in LDR constant-current sink could drive the 850 nm
  LED from 3V3 (register-logged drive current = rule-1 win; frees one FET);
  white/UV stay on 5 V.
- PDM mic: add 1 µF beside the 100 nF at VDD; tie L/R select explicitly;
  mono-left config (carry into IM69D130 re-verification).
- Piezo: pin drive H0H1; consider 470 Ω; ~1 MΩ bleed across the disc
  (piezo is a generator — handling/drops spike the pin); optional Schottky
  clamp. (Largely superseded if the piezo moves to a FET per M2.)
- MS5837-02BA: bind VDD to always-on 3V3; **no-clean flux, no IPA wash near
  U5** (datasheet: cleaning may damage it); power-up must be continuous (never
  GPIO-gate its rail); the -02BA01 metal lid is a *floating electrode* in the
  sample water — add an EC-vs-U5 coupling check to the calibration protocol;
  do not casually swap to the grounded-lid variant.

**ec-adc**
- Default gain 1/6 leaves only ~130–200 counts at range extremes → two-pass
  measurement (coarse at 1/6, re-acquire at max non-clipping gain), average N
  edge-synced samples, store gain/reference/TACQ/frequency with counts.

**rf-nfc-system**
- 300 pF NFC tuning caps are a placeholder (folded into M13).
- PDM clock (MHz-range, rail-to-rail) must not route near/parallel the
  high-impedance EC differential nets; place mic opposite the EC tongue;
  firmware stops PDM during EC bursts.
- Heater: reconcile R11 rating (spec "2 W" vs LIBRARIES "1 W 2512"; 0.25 W
  actual — either works, docs should agree); keep IMU/AS7341/mic off R11's
  copper pour (IMU zero-g drifts ±0.2 mg/°C — warm-up looks like tilt); only
  the DS18B20 shares the thermal island; gate tilt-wake reads away from heat
  pulses.

---

## 4. Fix list

Ordered: blocks-wiring first, then schematic content, then
bootloader/commissioning, then layout, then firmware, then docs.
**[MOOT]** = decision already made, action is execution only.
**[SWAP]** = already resolved or superseded by a decided part swap
(MT3608→TPS61023, LIS2DW12→LSM6DSO, MP34DT06J→IM69D130, E73→MDBT50Q-1MV2).

**Blocks wiring**
1. **[MOOT — execute]** Swap U1 in `puck-carrier.kicad_sch` from
   `puck-extra:E73-2G4M08S1C` to `puck-extra:MDBT50Q-1MV2` (+ footprint), fix
   the "BRAIN — E73" note, update `scripts/gen_schematic.py`, run Update PCB
   from Schematic. Spec pin map wires as-is — no remap. (C5)
2. Add U10 = XC6206P182MR 1.8 V LDO feeding **only** AS7341 VDD (3V3 in, ~1 µF
   in/out, keep 100 nF at the pin). I2C stays on the 3.3 V bus. (C1)
3. EC front end, before layout: mid-rail bias network (2×1 MΩ divider + 100 nF
   tap, 1 MΩ per electrode leg) **and** C1/C2 → 4.7 µF X7R 0805. (C3, C4)
4. FDC1004: add SHLD1 net — guard ring on the CIN1 trace + SHLD1 pour (L2 GND
   void) behind the 10 mm pad; SHLD2 NC; CIN2–4 NC no stubs; change spec
   "defined reference behind the FDC pad" from GND to SHLD1. (M6)
5. Add VBUS to the pin map: USB-C VBUS → module VBUS pad + decoupling (USB/DFU
   dead without it). (minors)

**Schematic content**
6. Q1–Q3: 2N7002 → AO3400A (drop-in; deletes a BOM line); confirm gate
   pulldowns so LEDs are off during boot/DFU. (M5)
7. Piezo off the GPIO: low-side FET switch + series R + bleed resistor across
   the disc. (M2)
8. **[SWAP — verify]** Boost = TPS61023: wire per its datasheet (EN logic from
   3.3 V *and* 1.8 V GPIO, FB divider drain, 5 V setpoint, inductor, output
   caps 0805/1206 16 V+); its load disconnect retires the MT3608
   always-live-rail/47 µA-bleed finding. (M4)
9. **[SWAP — verify]** IMU = LSM6DSO: tie CS and SDO/SA0 to VDD_IO, record the
   address (0x6A/0x6B — no bus clash) in the pin map; check INT default state
   for item 13's blacklist. (M8)
10. **[SWAP — verify]** Mic = IM69D130: verify PDM clock range vs the nRF
    default 1.032 MHz; if marginal, plan PDMCLKCTRL=1280K + Ratio80. Add 1 µF
    beside the 100 nF; tie L/R select. (M7)
11. Tie-offs and rail bindings: AS7341 GPIO → GND (never 3.3 V), INT/LDR NC;
    MS5837 VDD bound to always-on 3V3, never GPIO-gated; DS18B20 pull-up
    wording → "3V3". (C1, minors, refuted #4 salvage)

**Bootloader / commissioning (before the shell is sealed)**
12. Custom bootloader build only — **never a prebuilt hex**: board.mk gets
    `USE_NFCT = yes` (the Makefile defines CONFIG_NFCT_PINS_AS_GPIOS by
    default and burns NFC one-way on first boot). Gate: `nrfjprog --memrd
    0x1000120C` == 0xFFFFFFFF pre-dip. (M12)
13. board.h: BUTTON_DFU/FRESET on two spare unconnected GPIOs with test
    points; blacklist IMU_INT + PDM pins as button pins; add a small VDD-side
    LED_PRIMARY; CONFIG_GPIO_AS_PINRESET (P0.18). Extend the DFU gate to
    app-initiated OTA entry (only path after potting). (M15)
14. UICR REGOUT0: write 3V3 (`nrfjprog --memwr 0x10001304 --val 5`) at the
    one-time SWD flash; variant init guard (default→3V3→reset); commissioning
    gate "rail measures 3.3 V"; re-check after any eraseall. Decide 3V3 vs 3V0
    together with the M1 battery-floor policy. (C2, M1)
15. Puck variant: `USE_LFRC` (no LF crystal on module); bootloader based on
    the nice!nano build; never set DCDCEN0 (no LC on DCCH). (M3, minors)

**Layout**
16. BLE antenna keep-out ≥5 mm on **all four layers** + opposing-face
    component keep-out (MDBT50Q §2.3); boost hot loop diametrically opposite
    the antenna sector; optional free Raytac RF review. (M14)
17. NFC: draw the coil aperture first — all-4-layer void, ≥3–5 mm from magnet
    OD / LiPo foil / module shield / USB shell, ≥5 mm from antenna sector;
    tuning caps computed at layout, matched NP0, tuned after potting; fallback
    ferrite flex antenna or drop NFC. (M13)
18. Placement hygiene: mic opposite the EC tongue (PDM clock vs 100 kΩ
    differential nets); IMU/AS7341/mic off the heater pour (only DS18B20
    shares it); reconcile R11 rating across docs; GND kept around (not under)
    the FDC pad and mandatory around the I2C pins. (minors, M6)

**Firmware (write into the spec now; silently corrupts data otherwise)**
19. TX policy: default 0 dBm, cap +4 dBm unless the radio-vs-load interlock
    guarantees quiescent VDD loads during TX; System OFF budget <1 mA with the
    PDM clock stopped. (M2)
20. EC driver: TACQ = 10 µs (bench: `analogSampleTime(10)` today in
    `ec_bringup.cpp`); drive pins high-drive H0H1; idle range pin
    `nrf_gpio_cfg_default()` in the range-switch routine, both pins
    disconnected between bursts; edge-synced sampling (GPIOTE→PPI→TIMER→
    SAMPLE); per-range drive frequency (low 5–10 kHz, high ~1 kHz — respect
    the ≤10 kHz pad limit until the planned EC-drive pin-move); two-pass gain;
    discard ~1 s startup; log every acquisition setting with the raw counts
    (rule 1). (C3, C4, M9–M11, minors)
21. Log VBAT (VDDHDIV5) + VDD with every sample; battery-empty ≈ 3.5–3.6 V;
    flag FDC/DS18B20 samples with VDD <3.0 V; bench-measure actual REG0 output
    at commissioning. FDC1004: single-ended + CAPDAC, log CAPDAC. Sleep during
    charging so MCP73831 termination sees true battery current. (M1, M6,
    minors)

**Docs**
22. Stale-string sweep: `e73_puck` env → `mdbt50q_puck` (spec line 131),
    LIBRARIES.md line 8 "bare E73" → MDBT50Q-1MV2, update STATUS.md with the
    module swap + all decisions above; redo the 1:1 paper footprint check with
    the MDBT50Q land pattern before any JLCPCB order. (C5, workflow)
