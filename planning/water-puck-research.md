# Water Puck — Research Synthesis

*Compiled 2026-08-27 from five parallel research passes: sensors, radio, power/sealing/safety, market/prior art, build process.*

---

## 1. Verdict on the idea

**Genuine white space.** No consumer product exists that you drop *into* the water of an arbitrary container. Everything on the market is a bottle-integrated sensor, a cap, a clip-on, or a hold-near-the-water gadget.

- The exact device was patented in 2016 (**Thirsti Ltd, US20170336240A1** — in-container puck, pressure sensor at the bottom, BLE, accelerometer, wireless charging). **That patent has lapsed (expired, fee-related).** It's now prior art that protects you defensively rather than blocking you. Nothing else found looks blocking for a sealed submerged puck; a proper freedom-to-operate search is still worth it eventually.
- **Ecomo** (Kickstarter 2016, $638K raised) promised almost this exact sensor stack (TDS, TOC, turbidity, temp) in a bottle and died in hardware hell without shipping. Cautionary tale about scope.
- **HidrateSpark** — the closest namespace collision. Their "sensor puck" screws into the bottle base *from outside the water* (load cell). Their docs literally say "DO NOT submerge the sensor puck." After 10 years and Apple Store distribution, they do ~$4M/yr. **Hydration tracking alone is a small market.**
- **AquaPuck** (pre-Kickstarter, 2025/26) is circling the container-agnostic wedge right now — external clip-on load cell, not drop-in.

### Positioning (ranked beachheads)
1. **Filter-drift sentinel** — "your Brita/RO filter stopped working," via TDS drift. Rides the $6.75B US water-purifier market and proven TDS-pen behavior (HoneForest TDS pen: <$10, 16,000+ Amazon ratings — people already ritually dip TDS probes in their water; they just can't leave one there).
2. **Pet water bowl monitor** — anomaly detection maps to real vet concerns (drinking spikes = kidney/diabetes signals); gross-factor much lower; competitors (Felaqua ~$60) all require replacing the bowl — "works with your bowl" replicates the differentiator. Possibly #1 for go-to-market speed.
3. **Coffee/tea water nerds** — SCA water specs are TDS targets; small, high-ARPU, evangelical launch community.
4. **Cistern/tank/RV** — Mopeka already owns it from outside the tank at $40.
5. **Pure hydration tracker** — last. Ship it as a free feature, never the pitch.

### Lessons from the pool-monitor graveyard
pHin (acquired, shut down 2021, bricked devices), Sutro ($29–39/mo, discontinued 2025). Survivors: WaterGuru (consumables, **no subscription**), Ondilo ICO (replaceable probes). Pattern: **electrochemical probes drift and die; subscription-dependent water monitors get shut down; drift-tolerant sensing + no subscription survives.**

**BOM existence proof:** Xiaomi MiFlora — $10–15 retail, BLE, capacitive + EC + temp + light, 1-year coin cell, tens of millions shipped. EC sensing in a sealed consumer BLE puck at this price is proven.

---

## 2. The radio problem — solved, but not the way you'd guess

**Physics:** 2.4 GHz attenuates ~3.3 dB/cm in fresh water (measured BLE: –2.26 dB/cm RSSI), plus ~4–5 dB per air↔water crossing. Link budget gives **~10–13 cm of water max at 0 dBm; dead past 15–20 cm**. A puck under 25–30 cm of water in a full carafe cannot reach a phone through the water column. Also: **iOS does not support LE Coded PHY** — don't count on long-range mode for the phone link.

**Your "antenna faces down" instinct is correct and is the whole trick.** The phone doesn't need line-of-sight — it receives via multipath. Antenna radiates down through the glass/plastic base (few mm, negligible loss), leaks laterally out from under the container rim, diffracts around the room. ~15–25 dB excess loss vs free space → **several meters of real range**. HidrateSpark proves this exact geometry ships at consumer prices (~10 ft sync range).

**Design rules:**
- PCB horizontal, **ground plane on top (water side)**, antenna at board edge over a **sealed dry air cavity** facing the base. ≥5 mm antenna keep-out of air/low-εr plastic. **Never pot the antenna near-field** — leave a void.
- Don't try to match the antenna into water (radiation efficiency collapses to ~0.1–1%). Mechanically exclude water from the near field, then tune the match once in the final assembly with a VNA. Epoxy alone detunes chip antennas enough to cost ~50% range if ignored.
- **Store-and-forward is the core protocol**, not a fallback: timestamped log in flash, low-rate advertising always, **accelerometer-triggered advertising bursts on tilt/lift/refill** — every drink momentarily pulls water off the puck, creating natural sync windows several times a day. Only "live query of a full untouched jug" is lost, and the downward path covers that anyway.
- **NFC tag** on the puck: pairing + guaranteed tap-to-sync when washing/refilling. Cheap (tag emulation on MCU or dual-interface EEPROM).
- LED for pairing/reminders only, not data.
- **Steel bottles: no viable v1 path.** Faraday cage kills BLE *and* NFC. Say "glass/plastic only" loudly and early. Roadmap options: charging-coaster that doubles as a bridge, lid relay, or an integrated-bottle SKU (the HidrateSpark path).

---

## 3. Edited sensor list

### KEEP (v1)
| Sensor | Change from your list | Why |
|---|---|---|
| **MS5837-02BA** pressure | Use **-02BA** (0.2 mm resolution), not -30BA (2 mm — too coarse for sips) | Backbone of consumption tracking. **Gotcha: it's an absolute sensor** — barometric weather swings (±20–30 mbar over days) equal the whole jug's signal. Sips/refills are step changes → high-pass event detection works; absolute fill % needs the phone's barometer as reference during syncs. Not in JLC library (~$10.70 qty 1) — hand-place. Never let epoxy touch the gel port. |
| **EC electrodes** | **Not steel.** Gold ENIG PCB fingers or graphite; 316L as fallback. **Not DC** — bipolar AC 1–10 kHz from MCU GPIO. Measure at **3–4 frequencies** (100 Hz/1k/10k/100k) = free poor-man's impedance spectrum | Steel pins polarize, corrode, taste like pennies. TDS ≈ 0.5–0.7 × EC. Cannot distinguish Ca/Mg from Na — say "mineral load," not "hardness." Temp compensation (~2%/°C) mandatory. ~$0.20 total. |
| **AS7341 + white LED** | Add an **850 nm IR LED at 90°** for real turbidity (~$0.30) | Color + clarity, cheapest high-value channel. $5.57 LCSC, in stock, JLC-assemblable. Needs real optical windows in the pot, LED modulated to subtract ambient, channel *ratios* to cancel LED aging. |
| **365 nm UVA LED** | Keep the LED, drop the photodiode — **the AS7341's 415–480 nm channels are the fluorescence detector for free** | CDOM/organics channel for pennies. Correction: "biological activity" needs 280 nm excitation, not 365 — scope as "gross organic contamination/residue," experimental firmware flag. |
| **LIS2DW12** accel | Downgrade from LSM6DSO — you don't need the gyro | Same slosh gating, tap-to-wake, tilt-triggered sync, at $1 and 1–13 µA. |
| **FDC1004** capacitive | Keep; drop the "oil film" claim | Wet/dry through unbroken epoxy, $1.70, and a self-diagnostic: FDC says submerged + EC says open-circuit = electrodes fouled. |
| **Piezo disc** | **Buzzer only.** No sensing claims | Pressure already detects pours/refills quantitatively. Keep as find-my-puck/low-battery buzzer. |

### CUT
- **AD5933** — wrong tool without a serious 4-electrode AFE (bottoms out ~1 kΩ; tap water is below that; its DC bias electrolyzes electrodes; in 1–100 kHz dilute water is essentially resistive so the "spectrum" mostly re-measures EC + electrode artifacts). The multi-frequency GPIO EC sweep captures ~80% of the information at ~0% of the cost. v2 experiment with proper AFE + gold electrodes.
- **Optical pH patch** — real products (PreSens/PyroScience) but each spot covers only ~2–3 pH units, readout is referenced *fluorescence* (not colorimetric — reading with AS7341 is a research project, ±0.5 realistic), spots cost tens of € and photobleach in weeks–months. Drinking-water pH also carries little anomaly info EC doesn't. Not v1, not v2.
- **Heated resistor + NTC** — triple-redundant with EC/FDC/pressure for wet-dry, and the worst power citizen on the list (50–200 mW vs a ~100 µW system budget).
- **275 nm UVC pair** — defer to v2. Path-length math kills the naive version: clean tap water UV254 is 0.02–0.15 cm⁻¹ (standard method uses 1–10 cm quartz cells); at ~1 mm you're resolving 0.5–3% against LED thermal drift. Needs ≥10–20 mm folded path + dual-beam reference; solar-blind photodiodes (GUVC-T21GH) are $16 each and you need two. **The chlorine-proxy claim is wrong — drop it** (OCl⁻ absorbs at 292 nm weakly; literature says spectroscopic chlorine in real water is unworkable due to NOM interference). Legit v2 claim: relative "organic load changed."

### "Out of reach" list — confirmed
Lead, bacteria, nitrate, PFAS: all confirmed out (reagents/lab territory). Iron: quantitation out, but rust events show up as color+turbidity — a fair "something changed" proxy. **Add to the list:** hardness specifically (EC can't separate ions), fluoride, free chlorine as a number.

### Is "liquid fingerprint" anomaly detection sound? Yes, with the right claims
Published e-tongue work supports classification and change detection from cheap multichannel data (EIS clusters beverages; printed-electrode e-tongue + ML separated water/coffee/juice/wine at 100%; milk spoilage tracks impedance). Your channel set — temp-compensated multi-frequency EC + 10 spectral bands + NIR scatter + temperature — is a legitimate low-dimensional fingerprint. Engineering truths: (1) it works as a **per-jug relative baseline** ("this changed"), not absolute chemistry; (2) fouling causes slow monotonic drift — **detect steps, model drift**; (3) temperature is the #1 confounder; (4) let users label anomalies ("that's my fridge filter, it's fine"). The no-safety-claims framing is exactly right and keeps you out of EPA/NSF claim territory.

**v1 electronics BOM: ~$35–40 @ qty 10, ~$20–25 @ 1k.**

---

## 4. Power, sealing, safety

### Battery: CR2477 primary, seriously consider no charging at all
- System average ≈ 20–60 µA, **dominated entirely by BLE advertising** (slow to 2–5 s intervals + connect-on-demand → ~8–12 µA). Everything else duty-cycles to ~nothing.
- **CR2477 (1000 mAh, $2–3) → 2–3 years real-world.** No charging system, no swelling, no plating failure mode; pot it solid. Needs a 100 µF+ bulk cap to buffer radio pulses (15 mA pulse limit).
- **Avoid pouch LiPo**: cells outgas and swell with age; rigid potting gives gas nowhere to go — seams split, and a vent would put electrolyte (LiPF6 → HF traces) *into drinking water*. That's the disqualifying scenario, not fire.
- If rechargeable is a hard requirement: **LTO** (safest chemistry, no runaway mode, but tiny capacity — needs <10 µA) + **inductive charging through the epoxy** (what Oral-B/Sonicare do; 100–200 kHz link, TI BQ51003-class or LTC4124, ≤1 W so the potted puck doesn't cook). **Never pogo pins** (electrolysis in drinking water) or USB flaps (biofilm pocket).
- **Reese's Law (UL 4200A / 16 CFR 1263)** applies to any consumer product with a coin cell: abuse testing + warning labels, ~$3–8k. Potting helps compliance. A LiPo dodges Reese's Law entirely — a real argument, but the venting risk wins; take the CR2477 + compliance cost.

### Enclosure: Tritan shell beats pure potting
- **Best architecture: molded/machined Eastman Tritan shell (FDA FCN 1041, NSF 51, dishwasher-durable — the premium water-bottle plastic) as the food-contact surface + FDA silicone O-ring + interior epoxy backfill.** Then the epoxy never touches water and doesn't need food certification, and prototypes are serviceable.
- If potting the outside anyway: **Master Bond EP42HT-2FG** (FDA 21 CFR 175.300 + NSF 51) for the body; **EPO-TEK 302-3M** (optically clear, USP Class VI) for cast optical windows. Sapphire or borosilicate discs for scrub-proof windows.
- Potting exotherm can cook the cell — pot in thin stages, slow formulation, thermocouple the trials.

### Geometry
- 50 mm × 15 mm = 29.5 cm³ → must exceed 29.5 g to sink; epoxy+PCB+cell ≈ 35–40 g sinks *barely* and tumbles when pouring. **Target 50–60 g (SG 1.7–2.0) via a 316SS ballast ring** at the bottom perimeter (low CG, self-righting). Keep the steel ring out of any charging coil's flux path.
- FDA-silicone bumper ring: anti-slide, anti-rattle, glass protection. Chamfer everything.
- **Pour-out risk is real**: a puck slides out of a wide-mouth jug on the last inverted pour. Mitigations: ≥50 mm diameter, silicone friction, accelerometer "I've been dumped" phone alert, embossed "DO NOT SWALLOW — REMOVE BEFORE POURING," industrial non-candy color.
- **Dishwasher: forbid it, design to survive one accident** (CR2477 rated to 60–85 °C variants, Tritan is dishwasher-durable, Tg>100 °C epoxy). "Dishwasher-forgiving, not dishwasher-safe."

### Fouling
Biofilm within days on anything submerged 24/7; chlorinated tap suppresses it, filtered/RO water fouls faster. Consumer answer: **prescribed cleaning ritual** — weekly rinse + brush, monthly 10-min vinegar/citric soak (also descales electrodes), app reminders, and drift self-detection that nags the user. Never copper antifouling (leaches) in drinking water.

### Compliance budget (eventually, to sell)
Pre-certified BLE module inherits FCC intentional-radiator cert → only Part 15B (~$1–3k). CE/RED package $5–15k. BT SIG $9.6k (or piggyback module QDID). NSF/ANSI 51 $5–20k (the credible consumer trust mark). EU food-contact migration testing $3–10k. UL 4200A $3–8k. **Total ~$25–60k before scale — irrelevant for prototypes, budget it before any crowdfunding promise.**
**Claims:** stay in "hydration and water-freshness insights." FTC has a history with water-quality marketing; "detects contamination" is the danger lane. Your instinct to never claim safety is exactly right.

---

## 5. Build process — your plan, corrected

### "Skip breadboard" — half right
No breadboard, correct. But **v1 is NOT the 50 mm puck.** Seven subsystems on a dense first board you can't probe or bodge = classic first-board death spiral. Commit to the middle path:

- **M0 — Sensor exploration board** (~70–100 mm, 4-layer, USB-C powered + charges the battery path, every sensor populated, test points on every rail and I2C bus, 0Ω/DNP jumpers to isolate subsystems, SWD + UART headers). Exit criteria: every sensor streaming raw data over BLE, EC within ±5% on all three standards after cal, **DFU round-trip proven including rollback**, sleep current <50 µA measured. 2–4 months nights-and-weekends including the KiCad learning curve.
- **M1 — Form-factor puck, unsealed** (50 mm, battery, cut losers, antenna over the dry cavity). Exit: M0 bar in real geometry + BLE range measured sitting in a pot of water. 2–3 months.
- **M2 — Potted/sealed puck.** Potting trials on **dead boards first** (exotherm thermocouple, window clarity, MS5837 port masking, antenna detuning before/after) — 3–5 sacrificial pots. Then 2–3 live units on long soak tests against the reference meter. 2–3 months.

**Treat epoxy as a subsystem with its own milestone.** And: **OTA DFU is existential, not optional** — a potted device has no SWD. MCUboot + signed BLE DFU must be proven before the first drop of epoxy.

### Risk triage
- I2C-trivial (near-zero electrical risk): MS5837, AS7341 (risk is optical/mechanical), LIS2DW12, FDC1004.
- Genuinely risky, the reason M0 exists: **EC analog front-end** (3 decades of range from 84 µS to 12.88 mS standards — needs auto-ranging or two gain paths; cell constant is empirical), **antenna-in-final-assembly**, **the potting process itself**.

### MCU/firmware
- **Module, not bare chip — non-negotiable** (pre-certified, hand-solderable castellations, $4–12). **nRF52840 for M0** (deepest ecosystem, and USB — genuinely useful on the exploration board; nRF54L15 has no USB). Raytac MDBT50Q-1MV2, MinewSemi MS88SF3, or EBYTE E73 (~$4–6, hobbyist-proven). **nRF54L15 (Raytac AN54LV-15) is the production-revision candidate** — half the radio current, +8 dBm, smaller — once its module ecosystem matures for you.
- **Firmware: nRF Connect SDK** (= Zephyr + Nordic BLE stack + MCUboot/DFU tooling). Devicetree will annoy you for a week; it's a software person's kind of problem. Arduino core is a trap (weak low-power and DFU story). Rust/embassy is genuinely good but the signed-DFU path is DIY — side quest, not for the device that gets potted.

### JLCPCB realities
- 4-layer assembled, qty 5 (assemble only 2 — valid money-saving trick): **$120–250/spin**, 2–4 weeks landed.
- In LCSC library, assemblable: AS7341, FDC1004, AD5933 (if you want a DNP footprint), LSM6DSV/LIS2DW12, W25Q QSPI NOR. **Not in library: MS5837** (DigiKey; hand-place — it's a gel-port part that *should* be hand-placed anyway). nRF modules: intermittent stock — default plan: JLC places passives+sensors, you hand-solder the castellated module.
- **#1 assembled-board killer: rotation/pin-1 errors in pick-and-place data** — scrutinize JLC's component preview render part by part, especially ICs and diodes. Also: lock the BOM and order fast (stock churns), 0402/0603 not 0201, run DFM before paying, don't forget power LED + mounting holes + I2C address collisions.

### Your two rules — both correct, extended
- **Rule (a) raw data:** log raw counts **plus every acquisition setting that shaped them** (AS7341 gain/integration/which LED at what current, EC frequency and gain path, temps). Raw counts without acquisition parameters are as useless as derived values. Calibration = versioned blobs stored on-device and mirrored; every record carries firmware version + cal version + boot ID + monotonic sequence + CRC. Append-only binary (CBOR), littlefs on a $1–2 QSPI NOR (weeks of unsynced logging). Time: no RTC — uptime + boot ID, phone writes an (uptime, epoch) anchor on every connect.
- **Rule (b) calibration** — shopping list (~$150–200): EC standard *sachets* 84 µS / 1413 µS / 12.88 mS; NIST-traceable thermometer (temperature is the master calibration — EC moves ~2%/°C); DI water; 0.01 g scale + KCl (0.7455 g/L = 1413 µS — make your own standards as a cross-check); test-matrix liquids logged as regression fixtures (your tap, a labeled mineral water, saline series, juice, tea). **Skip the pH buffers — you no longer have a pH sensor.** Reference instrument: **Apera PC60 (~$150)** — every puck reading gets a same-timestamp reference reading, or ground truth doesn't exist. Protocol: temp-equilibrate, rinse DI then in next standard, low→high, re-check 1413 µS at session end to catch drift, derive cell constant K empirically (never trust geometry).

### Tools (~$450 must-have)
Pinecil iron, 858D hot air (mandatory for module rework), flux/wick/tweezers, multimeter, J-Link EDU Mini or nRF52840-DK ($50 — debugger + known-good reference), $15 logic analyzer + PulseView (decodes all your I2C problems — more useful than a scope here), cheap USB scope for the EC waveform. Strongly recommended: **Nordic PPK2 (~$100, the best battery-life tool that exists)**, nRF52840 dongle ($10) + Wireshark as BLE sniffer, thermocouple meter (potting exotherm), USB microscope ($30).

### Budget & timeline
**3–4 board spins, ~$1,500–2,500 total, 6–12 months nights-and-weekends.** The long pole is debugging time, not fab time — which is exactly why M0 must be probeable.

---

## 6. Top risks, ranked

1. **Antenna in the final potted geometry** — only testable with the real assembly; test potted early with sacrificial boards.
2. **Potting/sealing process** (exotherm, windows, gel port, food-contact) — treat as a subsystem.
3. **Biofilm/fouling drift** vs. anomaly detection — the algorithm must separate slow fouling drift from real steps, or the core feature false-alarms.
4. **Barometric confounding of level tracking** — solved by event-based detection + phone baro reference, but bake it into the algorithm from day one.
5. **Market: hydration is small** — lead with filter-drift / anomaly / pet-bowl positioning.

## 7. Immediate next steps

1. **Week-one physics test (before any PCB):** nRF52 dev board or dongle potted in a jam jar of epoxy, dry air pocket under the antenna, sunk in a glass jug — measure RSSI around the room. This retires risk #1 for ~$30.
2. Order calibration standards + Apera PC60 + tools.
3. Start M0 schematic in KiCad: nRF52840 module, MS5837-02BA, AS7341 + 3 LEDs (white/850/365), gold-finger EC + GPIO AC excitation, LIS2DW12, FDC1004, QSPI NOR, USB-C, battery path, test points everywhere, DNP AD5933 footprint if curious.
4. Prove BLE DFU round-trip on the dev kit before the board even arrives.
