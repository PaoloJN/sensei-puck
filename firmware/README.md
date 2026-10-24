# Sensei Puck firmware

The default target is `mdbt50q_puck`, the bare Raytac module on the carrier.
`puck` and `bench_*` target the XIAO bench board. Run PlatformIO from this directory.

```sh
pio run -e mdbt50q_puck -e puck
```

## Implemented

- Project-local board definition and 48-pin identity-map variant. Arduino N is
  P0.N; Arduino 32+N is P1.N. See `variants/mdbt50q_puck/variant.h`.
- `initVariant()` sets boost, heater, optical LEDs, piezo, ring data, status LED
  and EC bias low before enabling output drivers. Both EC drive pins stay Hi-Z.
- The variant programs an erased REGOUT0 voltage field to 3V3, preserves other
  bits and resets. It never erases UICR, touches NFCPINS or enables DCDCEN0.
- `USE_LFRC`, because the module has no external 32 kHz crystal.
- A commissioning idle image reports uptime, REGOUT0 and USB VBUS detection.
  A wrong non-default REGOUT0 setting reports `STOP_CHECK_3V3`.

Carrier, XIAO, I2C scan, RF beacon and EC bench builds passed on 2026-10-11.
No image was ever flashed to a carrier; no carrier was built.

## Not implemented

Sensor acquisition, calibrated EC, raw logging, BLE transfer, low-power scheduling,
charge-state management, watchdog recovery, an application and the custom bootloader
are unfinished. The bench sketches are experiments, not a production sensing stack.
The EC sketch uses sequential single-ended reads: it does not validate simultaneous
four-wire measurement, synchronous SAADC sampling or conductivity accuracy.

## Hardware rules for the application

- `PIN_EC_BIAS_EN` = P0.30. Keep low/Hi-Z when idle. For a measurement, enable
  bias, allow the network to settle, acquire a balanced AC burst, disconnect both
  drive pins and disable bias. Measure residual DC against exposed dock ground.
- MCP73832 STAT is open-drain, but high-Z means either full or undocked.
  Use `NRF_POWER->USBREGSTATUS.VBUSDETECT` for dock power; never infer it from STAT.
  Suspend sensing/radio/heater/ring while dock-powered and prove termination.
- Store counts and settings: ADC gain/reference/acquisition time, excitation
  frequency/range, CAPDAC, optical gain/integration/LED state, VDD/VDDH, uptime,
  boot ID and quality flags. Apply calibration downstream.
- Cap BLE TX at +4 dBm (0 dBm default), respect the REG0 external-current budget,
  stop PDM clocks before sleep, and measure the complete load in each state.
- Leave P0.09/P0.10 in NFC mode. No `CONFIG_NFCT_PINS_AS_GPIOS` or DCDCEN0.

## Commissioning and recovery

Use SWD for initial programming and keep the SWD/reset pads accessible. A custom
Adafruit bootloader with `USE_NFCT = yes`, LFRC, P0.18 reset, P0.01 DFU and P1.15
factory-reset pads was never built. Measure the sensor rail
and inspect UICR after first boot and every erase. Prove app-initiated DFU and
recovery from an invalid/crashing application before sealing; a working-app-only
update path is insufficient.
