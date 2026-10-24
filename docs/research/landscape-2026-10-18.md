# Landscape: who already built "a device that tells you about the water in a container"

Date: 2026-10-18. Web survey after the decision to stop the v2 sealed puck
layout. Purpose: find what shipped, what failed, and where the gap is, before
choosing the v3 form (float, pen or clip).

## Shipped products

| Product | Form | Measures | Radio / app | Price | Notes |
|---|---|---|---|---|---|
| Xiaomi Mi TDS pen | dip pen | conductivity as TDS ppm, temp-compensated | none | $7–25 | The incumbent. No logging, no reference. |
| WaterH (Kickstarter 2023, shipping) | own steel bottle, TDS sensor in the bottom | TDS at every refill, intake | BLE, app, light ring, wireless charging | ~$80–100 | Closest commercial version of the Sensei Cup / v2 puck idea. Works because they own the bottle (sealing, antenna, charging are theirs). "99 % accuracy" is marketing. |
| HidrateSpark PRO | sensor puck screwed to the outside of the base | intake (level through the wall) | BLE, app, glow | ~$60–80 | Proves outside-the-wall sensing ships. Not a quality sensor. |
| Blue Connect / Blue by Riiot (now Fluidra) | floating pool monitor, antenna up | temp, pH, ORP, conductivity | BLE/WiFi, app | ~$300+ | The float architecture, proven in pools. CES award. |
| YINMIK BLE-YC01 | floating 6-in-1 | pH, Cl, ORP, TDS, EC, temp | BLE 5.2, app, logging, export | ~$50 | IP67, 3×AAA, months of battery at a 4-min poll. Lists "drinking water" as an application. Pool-sized. |
| Hanna HALO / HALO2 | lab pH probe with Bluetooth in the head | pH, temp | BLE, Hanna Lab app, calibration, logging | $150–250 | The professional "probe + phone" architecture: head in air, only the electrode wet. |
| WaTalk (Kickstarter 2022) | a cup you pour water into | turbidity ±0.02 NTU | BLE, app, compares to EPA/WHO | ~$100 | Literally a Sensei Cup, single parameter. |
| Lishtot TestDrop Pro | keychain, held next to the glass | claims 20 contaminants incl. bacteria, contactless, via "electric field" | LED only | $50 | Only promotional coverage found. No independent validation. Cautionary tale: claims without references. |
| Ecomo bottle (Kickstarter 2016) | bottle that tests and filters | TDS, TOC, turbidity → "bad/moderate/great" | BLE, app | $453k raised from 1,667 backers | Company pivoted to enterprise (Smart Fount, Red Dot 2025). Could not confirm whether backers received bottles. |

## Open source and DIY

- **Public Lab Riffle**: Atmel328 logger that fits through the mouth of a
  plastic water bottle, with the "Coqui" conductivity + temperature board,
  about $100, microSD, deploy then retrieve. The open-source cousin of the
  puck. No radio by design.
- **ESP32 + DFRobot TDS + DS18B20**: dozens of tutorials (how2electronics,
  electroniclinic, Blynk dashboards, a XIAO ESP32-C3 turtle tank). This is
  what the original Sensei Cup team built.
- **Academic**: Mezzera et al. 2018 (Polimi) low-cost pipe monitor with
  pH, temp, conductivity and a fouling-thickness sensor; a 2023 systematic
  review of low-cost IoT water sensors (PMC10181703). Interdigitated
  capacitance conductivity sensors on PCB (Javeriana). A Japanese smart
  bottle (level + temp + gyro) is the only "how long has it been sitting"
  device found, and it is a paper, not a product. Stagnation detection
  otherwise exists only as patents (US10309809, US7417417).

## What the landscape says

1. **Every consumer "water quality" device is a conductivity meter in a
   costume.** TDS pens, WaterH, Ecomo's headline number. Filter companies
   themselves (LARQ, Berkey, Epic) publish pages saying TDS is not safety.
   The project's "no safety claim" rule is correct and, stated openly, a
   differentiator against Lishtot-style claims.
2. **Only two architectures ship.** (a) A sensor in the bottom of a bottle
   the company controls (WaterH, Ecomo, HidrateSpark). (b) A head in air
   with the wet part below: floating (pool monitors) or a probe (Hanna).
   Nobody ships a throw-in tag for arbitrary containers, for the physics
   reasons already logged (water and steel kill 2.4 GHz). The v2 puck was
   trying to be (a) without owning the bottle.
3. **"Measure at every refill, sync when the phone is near"** is exactly
   WaterH's behaviour, so the interaction model is validated.
4. **The gap is time.** Nobody sells "this water has been sitting 31 hours
   at 24 °C" for the jug, pitcher, dispenser or pet bowl. Conductivity plus
   temperature plus a refill detector gives it for free.
5. **Price anchor.** A floating 6-in-1 with an app is $50 on Amazon. A
   project that only re-makes that is not interesting; one that adds
   references, raw data, open hardware and the stagnation timeline is.

## Consequence for v3

- Do not build another TDS pen, bottle or pool float.
- Build for the container you pour from, not the one you sip from.
- Form: either a small self-righting float (YINMIK and Blue prove the
  architecture; ours is pitcher-sized) or a rim probe with the head in air
  (Hanna proves it). Decide after the bench week, not before.
- Thesis for the report: referenced conductivity and temperature, raw
  counts with acquisition settings, plus the refill/stagnation timeline,
  validated against KCl standards and a week in a real jug.

## Sources

- WaterH: https://www.outdoorvancouver.ca/waterh-smart-bottle-review , https://www.bustle.com/wellness/smart-water-bottle-waterh-vita-review , https://manuals.plus/asin/B0C2CJM5KQ
- HidrateSpark puck: https://hidratespark.com/products/hidratespark-pro-led-bluetooth-sensor-puck
- Blue by Riiot / Fluidra: https://aquamagazine.com/community/belgian-start-up-riiot-labs-joins-fluidra.html , https://www.eurospapoolnews.com/news-en/53423.htm
- YINMIK BLE-YC01: https://www.winwinpoolshop.com/en/product/61401-93423/yinmik-ble-yc01-smart-pool-monitor-6-in-1-smart-floating-water-monitor-bluetooth-52-app-supported , https://f-droid.org/en/packages/com.yinmik.waterquality/
- Hanna HALO: https://hannainst.com/HALO , https://pacetoday.com.au/worlds-first-professional-ph-probe-featuring-bluetooth-smart-technology/
- WaTalk: https://www.businesswire.com/news/home/20220315006156/en/This-Kickstarter-Campaign-is-Funding-a-Cup-That-Can-Test-Water-Quality
- Lishtot: https://techcrunch.com/2018/01/11/lishtots-testdrop-tells-you-whether-water-is-safe-to-drink-without-even-touching-it , https://nocamels.com/2018/01/lishtot-safe-water-device/
- Ecomo: https://www.kickstarter.com/projects/ecomo/ecomo-the-worlds-first-bottle-that-tests-and-filte , https://www.red-dot.org/project/ecomo-smart-fount-22251 , https://app.dealroom.co/companies/ecomo
- Xiaomi TDS pen: https://www.richardbarrow.com/2019/03/review-of-xiaomi-mi-tds-water-quality-tester-pen/
- Riffle: https://publiclab.org/wiki/revisions/riffle/27819 , https://blog.oshpark.com/2016/04/10/riffle-open-source-data-logger/
- DIY ESP32: https://how2electronics.com/iot-based-drinking-water-quality-monitoring-with-esp32/ , https://www.electroniclinic.com/tds-sensor-and-esp32-iot-based-water-quality-monitoring-system/
- TDS is not safety: https://www.epicwaterfilters.com/pages/what-does-tds-in-water-mean-why-a-tds-meter-will-not-tell-you-if-it-is-safe , https://basq.livelarq.com/wellness/dont-use-tds-meters-to-measure-water-quality/ , https://support.berkeywater.com/about-tds-meters/
- Academic: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10181703/ , https://re.public.polimi.it/handle/11311/1078463 , https://patents.google.com/patent/US10309809
