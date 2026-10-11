# Water Puck POC — Shopping List (~$165 core, $300 ceiling)

Order everything in one sitting. AliExpress items take 2–4 weeks — order those FIRST, start firmware on the XIAO bench mule while they ship. Board-mounted parts (module, sensors, passives) are listed in `hardware/carrier-board-spec.md` "Full parts list"; this page covers the rest.

## Order now (the slow stuff — AliExpress unless noted)

| # | Item | Where / search term | Est. | Notes |
|---|---|---|---|---|
| 1 | **Seeed XIAO nRF52840 Sense ×1** | seeedstudio.com SKU 102010469, or Amazon/Mouser/DigiKey | $16 | Bench mule for firmware bring-up and the jug RF test. NOT on the board (the MDBT50Q module is). |
| 2 | **MS5837 pressure breakout** | AliExpress: "MS5837-30BA pressure sensor module I2C" | $10–14 | Usually the -30BA (2 mm resolution). Fine for pour/refill detection. Check photo shows the gel-filled metal cap. |
| 3 | **AS7341 spectral breakout** | AliExpress: "AS7341 spectral color sensor module" (~$9) or Adafruit #4698 ($16, faster/safer) | $9–16 | Adafruit version has better docs + Stemma connector. |
| 4 | **LEDs**: white 5 mm, 850 nm IR 5 mm, 365 nm UV 5 mm | AliExpress/Amazon: "5mm IR LED 850nm", "5mm UV LED 365nm" (small bags) | $6 | Get true 365 nm, not 395–405 nm "blacklight" — check listing. |
| 5 | **PROTECTED LiPo 3.7 V 400–500 mAh** with JST-PH | Amazon/AliExpress: "3.7V 400mAh lipo protected JST" | $6–8 | Must have protection PCB — it gets potted. |
| 5b | **Adafruit 5412 — magnetic 4-pin USB DATA cable** ×2 | adafruit.com/product/5412 | $10 | THE dock cable: charge + USB DFU/serial through the magnet. Pads copy ITS geometry (2.54 mm pitch). |
| 5b2 | Adafruit 5413 magnetic connector pair | adafruit.com/product/5413 | $7 | Dimensional reference + plan-B (pot the flat half flush in the epoxy face). |
| 5b3 | N52 disc magnets Ø5×2 mm (small pack) | Amazon: "5x2mm N52 disc magnets" | $6 | Two per puck, opposite polarities out = reversal keying. |
| 5d | **Raytac MDBT50Q-1MV2** ×2 | DigiKey "MDBT50Q-1MV2" (order WITH the MS5837) | $22 | The brain. Best-documented nRF52840 module; one for the board, one spare. |
| 6 | **Passives kit** (if you don't have): 0603/0805 resistor + capacitor book | AliExpress: "0805 resistor capacitor sample book" | $10 | Need: ~1 kΩ–1 MΩ resistors for EC ranging, 100 nF/10 µF caps, 2× small-signal caps for EC AC coupling. |
| 7 | **KCl (potassium chloride), lab/food grade ≥99%** | Amazon: "potassium chloride powder 99%" | $10 | 0.7455 g/L in DI water = 1413 µS/cm @25 °C — your homemade EC standard. |
| 8 | **0.01 g pocket scale** | Amazon: "0.01g digital pocket scale" | $12 | For making standards. |
| 9 | **TDS pen** | Amazon: "HoneForest TDS meter" (or any 4.5★ clone) | $12 | Your reference instrument. Sanity-checks every EC number the puck produces. |
| 10 | **Distilled water 1 gal** | grocery store | $2 | Near-zero EC point + mixing standards. |

## Max-sensor demo extras (~$15 — "20+ sensing channels" build)

| # | Item | Where / search term | Est. | Notes |
|---|---|---|---|---|
| E1 | **FDC1004 breakout** | AliExpress/Amazon: "FDC1004 capacitive sensor module" | $10 | Through-shell water sensing. I2C addr 0x50 — shares the bus, no conflict. |
| E2 | **DS18B20 waterproof probe** | AliExpress: "DS18B20 waterproof temperature probe" | $2 | Precision temp #2 + readout for the thermal-flow trick. 1-wire on D9. |
| E3 | **Power resistor** (~100 Ω, 1–2 W) | passives kit / any | $0.10 | The "heater": pulse it, watch DS18B20 cooling curve → stirring/flow detection. Demo-only, power hog. |
| E4 | **Piezo disc 20–27 mm** | AliExpress: "27mm piezo buzzer disc" | $0.30 | Buzzer: find-my-puck, score-alert chirp, tap-reply demo. Solders to the two PZ1 pads. |
| E5 | **NFC flex antenna, 13.56 MHz, ferrite-backed, ~20–30 mm, 2 wire leads** (or 30 AWG magnet wire to wind ~1 µH yourself) | DigiKey/Mouser: "NFC antenna flexible ferrite" (Molex / Pulse / Abracon); AliExpress: "NFC flexible antenna ferrite" | $3–8 | Solders to the two L2 pads on the bottom face; ferrite side toward the LiPo. Retune C12/C13 after assembly. |

## Shell & mechanical (~$30)

| # | Item | Where | Est. | Notes |
|---|---|---|---|---|
| 11 | Clear round waterproof container, ~55–70 mm, screw top with O-ring/gasket | Amazon: "clear waterproof pill container o-ring" or "small round clear waterproof case" | $8–12 | POC shell. Alternatively 3D-print body + clear acrylic disc lid if you have printer access. |
| 12 | 316 stainless washers (large, flat) | hardware store / Amazon | $5 | Ballast — target ~55 g total puck weight. |
| 13 | O-ring assortment + food-safe silicone sealant (small tube) | Amazon | $8 | Sealing the MS5837 port and any pass-throughs. |
| 14 | 5-min + slow-cure epoxy (small tubes) | hardware store | $8 | Spot-sealing only, NOT potting. |
| 14b | **IP68 acoustic vent membranes** (PTFE adhesive discs, small) | AliExpress/Amazon: "IP67 IP68 acoustic vent membrane sticker" | $5 | Covers the mic inlet — sound in, water out. Buy a sheet of spares. |

## The custom PCB (order after bench validation — week 3–4)

| # | Item | Where | Est. | Notes |
|---|---|---|---|---|
| 15 | Carrier PCB, 5 pcs, **4-layer, ENIG, black mask**, JLC assembly both faces ×2 | JLCPCB | ~$60–90 shipped | ENIG is mandatory (gold EC pads ARE the sensor). Assembly both faces because U8 (LGA) and U4 (0.5 mm VSSOP) sit on the bottom. See carrier-board-spec.md "JLCPCB order". |

## Tools — use the college labs instead of buying

Campus resources to hunt down (EE/makerspace/chem labs typically have all of these):
- **EE lab / makerspace**: soldering station, hot air, oscilloscope (EC excitation waveform), logic analyzer (I2C debugging), bench supply, multimeter, 3D printers (shell!), maybe a VNA (antenna check — ask, this is gold).
- **Chem/bio lab**: DI water, lab-grade KCl, **analytical balance** (0.0001 g — better than anything you'd buy), possibly a **calibrated conductivity meter and pH meter** (replaces the $150 Apera entirely — ask a lab tech), maybe a benchtop spectrophotometer (validates the AS7341 and any future UV254 claims against a real instrument).
- **Department budget**: if any funding is available, the priority upgrades in order: (1) MS5837-**02BA** breakout or bare part (10× finer level resolution → real sip detection), (2) a second assembled spin, (3) Apera PC60 for take-home reference measurements.

## Explicitly NOT buying (deferred)

- Apera PC60 reference meter ($150) — TDS pen + KCl standards cover the POC.
- FDC1004 breakout — EC pins do wet/dry detection.
- nRF52840 DK ($50) — XIAO bench mule + USB serial logging covers it; add a $10 nRF52840 dongle later only if you need BLE sniffing.
- pH anything, UVC anything, Qi charging, potting epoxy in volume.

**Running total: ~$165 core + ~$30 shell + ~$25 PCB = ~$220. Tools push worst case to ~$280.**
