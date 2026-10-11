# Water Puck — Product Story

*The narrative layer. The engineering lives in `hardware/carrier-board-spec.md`;
this doc is what the app, the demo, and the presentation are built from.*

## The one-liner

**An AirTag for water.** Drop it in any jug, bottle, or bowl you already own.
It sinks, watches, and only speaks when something matters.

> "A LARQ sterilizes water it knows nothing about.
> The puck knows everything about water — in any container you already own."

## The rule that shapes everything

**A feature only exists if it triggers a push notification a normal person acts
on.** The puck collects ~30 measurement channels; the user sees six sentences.
Everything else lives behind a "details" tab (evidence for nerds and
professors, invisible to everyone else).

## The six features (in the user's language)

1. **"This water's been sitting 3 days — dump it and refill."**
   Stale-water guilt, converted into one nudge. *(engine: freshness score —
   time-since-refill × temp history × clarity/EC drift × fluorescence)*
2. **"Your filter stopped working 2 weeks ago. You've been drinking unfiltered
   since."** The most useful sentence the product says. Unknowable today
   without a TDS-pen ritual. *(engine: TDS drift across refills vs learned
   baseline)*
3. **"Time to wash this bottle."** The puck actually measures the slime
   forming — the viral "dirtier than a dog bowl" anxiety, answered with data.
   *(engine: monotonic EC/optical drift = biofilm)*
4. **"Something changed your water."** A guard, not a chemistry lesson.
   Different source, something dissolved, cloudy overnight. User taps
   "that's fine — new filter" and the puck learns. *(engine: anomaly detection
   on the full fingerprint; user labels train the per-container baseline)*
5. **Silent hydration.** Zero logging, ever. Weekly: "you drank 30% less than
   usual." *(engine: pressure-step sip/refill detection)*
6. **Care Mode.** *"Dad's water jug hasn't been touched since yesterday
   morning."* Precedent: Japan's Zojirushi i-POT kettle — elder-care
   infrastructure disguised as a kettle, beloved for decades. Dehydration in
   the elderly is a real clinical problem; drinking-pattern change is a real
   early signal (same for pets — "is he drinking more?" is a standard vet
   question). The puck does this passively, in whatever jug/bowl they already
   use. **The feature that makes a demo audience feel something.**

## The glow ring (the only on-device UI)

- **Green** — all good. What it says 95% of the time. The product's default
  state is silence.
- **Amber** — refill or wash me.
- **Blue pulse** — syncing / tap acknowledged.
- **Red** — something changed; check the app.
- No screens, no buttons. Tap the jug twice → puck chirps (find-me + "I'm
  alive"). NFC tap → instant pair/sync.

## Demo script (in order of gasp)

1. **Liquid ID:** three glasses — water, Gatorade, salty water. Drop the puck
   in each; the phone names them in seconds.
2. **The guard:** volunteer secretly stirs sugar into "plain water" while the
   phone is face-down. Turn it over: *"Something changed your water."* (The
   thermal channel catches what conductivity can't — sugar barely conducts.)
3. **Sip tracking, live:** pour a glass; the level graph steps down in real
   time; daily total updates. Nobody touched anything.
4. **Care Mode story:** don't demo it — *tell* it. The i-POT story, then:
   "the puck does this for any grandmother's jug, any dog's bowl."
5. **Kill shot for questions:** "How is this different from a smart bottle?" →
   it works in the container you already own; the category leader after 10
   years does ~$4M/yr selling bottles; nobody ships a drop-in. Patent on the
   idea lapsed. We checked.

## What we deliberately do NOT say

- Never "safe" / "clean" / "pure" — the puck detects **change**, not safety.
  Saying so out loud is what makes the rest credible (and keeps us out of
  EPA/FTC claim territory).
- No germ-killing (that's LARQ's actuator game; open-container UV-C fails on
  eye safety, dose physics, and pesticide-device regulation — see
  design-review record).
- Bacteria / lead / PFAS: physically out of reach at this size. Owning this
  limit is a presentation strength, not a weakness.

## Calibration as ritual (rule #2 made user-facing)

- **Ice-point:** drop the puck in ice water → app captures a true 0.0 °C
  reference. Free, satisfying, scientifically legitimate.
- **The KCl one-shot:** guided "calibration ritual" against the homemade
  1413 µS/cm standard — great demo moment, real metrology.
- **Teach-by-tap:** every "that's normal" label improves the anomaly detector.
  The product gets smarter the longer it lives in your jug.

## Positioning map (from the market research)

| They | Do | Can't |
|---|---|---|
| HidrateSpark | weighs its own bottle | know anything about the water; work in your jug |
| LARQ PureVis | UV-zaps blind, own bottle only | measure anything at all |
| TDS pens ($10, millions sold) | one number, manually | live in the water; see color/clarity/patterns |
| Pool monitors | real sensing | fit in a jug; survive a consumer price |
| **Puck** | **knows the water, any container, passively** | **treat water; claim safety** |

## Second act: the aquarium (added 2026-08-31)

Same puck, sticker upgrade, second market. Aquarium keepers accept maintenance
rituals and consumables (Seneye: $140-210 + ~$10/mo colorimetric slides) — and
our optical cluster can read any colorimetric indicator patch placed in its
view. **Indicator patch mode:**

- **Seachem Ammonia Alert badge (~$10/yr)** in front of the AS7341 → continuous,
  logged, alarmed free-ammonia readings — THE fish-killer parameter.
- pH indicator patch → continuous ~±0.3 pH, Seneye-grade, monthly swap.
- Plus what the puck already does, repointed: temp alarms (critical for fish),
  salinity/EC drift, algae-bloom early warning (fluorescence + turbidity
  trends), evaporation top-off reminders, Care Mode for livestock.

Pitch line: "Seneye charges a subscription for a slide reader. The puck reads
the $10 badge you can already buy — in any tank, forever."

No hardware change. Real glass-electrode pH remains a documented v2 option for
the tank variant only (spare AIN4 + one op-amp; tank life solves the
wet-storage problem that kills pH in the kitchen version).

## v2 concept log: the dock as a platform (added 2026-08-31)

- **Wired mode (tanks/installations):** the 4-pad dock already carries USB —
  leave the magnetic cable attached and the puck runs on shore power with
  wired data streaming; BLE becomes the backup. Constraint: the magnetic
  joint must stay DRY (docked pads are live) — mount the puck with the dock
  face above waterline / against dry glass, or permanently seal the cable at
  potting (then it's a corded tank probe SKU).
- **Magnetic accessory port ("MagSafe for water sensors"):** a second pad
  constellation carrying switched 3V3 + I2C, so external potted modules
  (glass pH, dissolved oxygen, ORP) snap on magnetically. Requires a
  power-gated port (bare I2C pull-ups would bias wet pads — same physics
  that killed dock-SWD) + presence detect. v2 hardware; the flagship
  expansion story.
