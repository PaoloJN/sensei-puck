# Spin 1 validation and release gates

No physical gate has passed: no hardware has been purchased or assembled.
Record date, board serial/revision, firmware hash, instrument/reference ID, setup,
raw files and result for every test. Preserve failed results as well as successes.

## Before fabrication

- ERC: no errors; review each warning. PCB DRC: no errors, no unconnected items,
  no schematic mismatch; do not suppress a violation to meet this gate.
- Review actual copper and soldermask Gerbers on all four layers, board outline,
  drills, polarity, assembly side/rotation and charger/boost bypass loops.
- Verify each selected MPN against its package drawing. Print 1:1 and compare
  the module and actual dock mate. Confirm ground, D+, D− and 5V by continuity,
  viewing the correct mating face; test both attempted docking orientations.
- Confirm assembler can populate the µSOP/LGA parts on both sides, accepts the
  exposed electrodes and meets the complete budget including shipping and tax.

## Unsealed electrical bring-up

1. Inspect shorts/polarity with battery disconnected. Start from a current-limited
   supply. Verify the dock diode direction and no VBUS-to-battery backfeed.
2. SWD-program the bootloader and commissioning image. Check UICR NFCPINS,
   REGOUT0, reset configuration and the actual 3V3/1V8 rails before enabling loads.
3. Measure battery and sensor rails across a controlled discharge and radio/load
   transients. Set the usable battery floor from the measured rail, not a guessed
   remaining-charge percentage. Verify external-current limits in every state.
4. Verify reset/bootloader leave boost/heater/LEDs/EC disabled. Scope boost startup,
   output ripple and shutdown; check inductor, charger and heater temperatures.
5. Charge at the selected 100 mA setting; log cell/charger temperature and current
   at low battery, termination, recharge and unplug. Prove the firmware suspends
   loads based on VBUS even when STAT is high-Z. No load-sharing IC is fitted.
6. Check USB enumeration, serial traffic and DFU through the actual dock, including
   plug/unplug cycles. Inspect D+/D− waveform or errors if connection is unreliable.

## Measurement and immersion development

- EC: scope both electrode polarities, net DC and current to exposed dock ground
  while undocked. Compare two-/four-electrode results against at least two
  independently checked conductivity standards and temperature. Test both ranges,
  startup settling, bubbles, movement, long immersion and cleaning. Validate SAADC
  source impedance/acquisition timing; the bench sketch is not this validation.
- Optics: dark/ambient/white/IR/UV captures with gain and integration settings.
  Compare empty cell, reference liquid, bubbles and residue. Test cured resin and
  shroud samples for fluorescence, crosstalk and attenuation before coating LEDs
  or AS7341. Turn the glow ring off during acquisition.
- Pressure: calibrate against known water-height changes and a reference pressure
  or level measurement. Test movement and temperature. Conversion to volume is
  container-specific; pressure drop is not a measured sip.
- Temperature/heater: compare against a reference at several temperatures. Measure
  response lag and heater coupling at the actual sensor location before claiming
  flow or liquid identification. Enforce a bounded heater pulse and cooldown.
- FDC: log raw counts and CAPDAC for dry/wet, bubbles and coating thickness.
  The concentric coplanar electrodes do not provide two water-height samples.
- RF: full/half/empty jug, orientations and intended phone position, with actual
  battery, ballast and enclosure. Measure packet loss and successful backlog
  transfer, not RSSI alone. Keep metal and resin out of the antenna air cavity.
- Sealing: first test a nonpowered dummy. Define port, membrane, electrode and
  dock seals mechanically. Leak-test repeated immersion/dry/charge/clean cycles;
  masking the pressure port or microphone inlet does not waterproof their PCB joints.

## Before any permanent sealing

Prove normal OTA, interrupted update recovery and recovery from an application
that crashes before advertising. If the bootloader cannot recover without the
application, retain a sealed service-access design for SWD/reset. One successful
OTA transfer is insufficient evidence to bury the debug pads.

Keep one unsealed reference unit. Keep the battery out of rigid epoxy and provide
mechanical room for it; charging temperature and repair access remain enclosure
constraints. Test liquids remain laboratory samples until material compatibility
and the intended contact use have been separately established.
