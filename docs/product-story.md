# Water Puck — demonstration scope

An experimental puck for recording changes in water in a glass or plastic
container. The proposed demonstration compares raw optical, conductivity,
temperature and pressure measurements with reference instruments. The hardware
has not been assembled, calibrated or tested in water.

## What the first demonstration should prove

1. Record repeatable raw readings, with timestamps and acquisition settings.
2. Distinguish measured samples in a controlled experiment using held-out trials.
3. Relate pressure changes to known additions/removals of water in one calibrated
   container. Removed volume is not evidence that somebody drank it.
4. Retrieve records and recover firmware reliably, including after a failed update.

A classifier, phone app, freshness score and notifications are future software.
Define their accuracy from data before writing a demonstration script around them.

## Claims that need evidence

| Proposed feature | What the current design can establish |
|---|---|
| Filter replacement | Conductivity may change; filter effectiveness needs a filter-specific reference test. |
| Biofilm detection | Optical/EC drift has many causes, including residue, bubbles, temperature and sensor fouling. It does not identify biofilm. |
| Sugar detection | Thermal/optical response is an experiment. The heater and temperature sensor are separated; sensitivity has not been demonstrated. |
| Hydration or care alerts | Pressure records container level, movement and ambient pressure. It cannot establish ingestion or a person's condition. |
| Aquarium alarms | Patch optics, calibration, immersion life and drift require separate validation. No quantitative ammonia/pH performance is established. |
| Universal containers | Start with one clear, nonmetallic jug. Geometry, wall material and water depth affect optics and BLE. |

The puck does not assess drinking-water safety or identify pathogens or contaminants.
Use test liquids for commissioning. A green light should mean “recording” or
“connected”, never “safe to drink”. Amber can mean “measurement unavailable”; blue
can mean “syncing”. Reserve anomaly indications for validated comparisons.

Earlier presentation concepts are preserved in
[the paused baseline](history/2026-09-paused-baseline/product-story.md).
