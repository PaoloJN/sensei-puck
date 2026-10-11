# Water Puck carrier specification — October revision

This document supersedes the paused September specification, preserved in
`../docs/history/2026-09-paused-baseline/`. See `../STATUS.md` for the actual
routing and check status. Hardware performance has not been validated.

## Board and assembly

Ø46 mm, four copper layers, 1.6 mm nominal thickness, ENIG and black soldermask.
Board center (150, 100) mm. Sensor face is F.Cu; the Raytac module and most
support circuits are on B.Cu. Two-sided assembly is required. Seven fiducials
and test pads are not purchased electronic components.

Keep the antenna sector free of copper and nearby battery/ballast/magnets.
The concentric FDC electrodes have a driven SHLD1 plane beneath them; retain
its isolation from ground and the inner-layer EC/optical sensing keep-outs.
The editable PCB and its rules, rather than old renders, define the geometry.

## Power and charging

- U1 MDBT50Q-1MV2 uses battery-powered VDDH. Its REG0 output feeds the 3V3
  sensors. Program REGOUT0=3V3 and measure the actual rail over discharge;
  samples outside sensor supply limits need quality flags. Keep DCCH open
  and never enable DCDCEN0. Use LFRC; there is no external 32 kHz crystal.
- Respect the nRF52840 external-current budget (including GPIO loads).
  Firmware targets 0 dBm TX, +4 dBm maximum, and stops PDM before sleep.
  A runtime/load budget remains a measurement gate, not a completed result.
- U7 **MCP73832T-2ACI/OT** (open-drain STAT), R17 **10 kΩ**, approximately
  **100 mA** charge current. C24/C25 **10 µF / 16 V X7R, 1206, TDK C3216X7R1C106K160AC**
  on VBUS/VBAT. Confirm effective capacitance and placement
  against the charger datasheet. There is no power-path/load-sharing circuit.
- Use USB VBUS detection to suspend active loads while dock-powered. STAT
  high-Z means either charge complete or unplugged. It cannot establish dock
  presence. A 73831 substitution would expose the MCU to STAT driven near VBUS.
- U2 TPS61023: L1 **SWPA4030S1R0NT**, 1 µH; C5/C6 22 µF / 16 V 0805;
  R15/R16 750 kΩ / 100 kΩ, nominal output about 5.06 V. R33 **100 kΩ**
  pulls BOOST_EN low during reset. Check MLCC bias derating and ripple.
- U10 XC6206P182MR feeds **only AS7341 VDD at 1.8 V**. C14/C15 are 1 µF;
  C7 is the local bypass. I2C pulls up to 3V3.
- Use a protected LiPo whose manufacturer allows the selected charge current.
  Keep the battery replaceable during development and out of rigid epoxy.

## Magnetic dock

Adafruit 5412 four-contact cable, 2.54 mm pitch, Ø2.0 mm PCB contacts.
In PCB **top-coordinate view**, increasing x at y=118 mm:

| Ref | x (mm) | Net |
|---|---:|---|
| CP1 | 146.19 | GND |
| CP3 | 148.73 | D+ (/PAD_DP) |
| CP2 | 151.27 | D− (/PAD_DM) |
| CP4 | 153.81 | +5V (PAD_5V) |

Bottom view mirrors this row. Confirm the physical mating-face orientation and
continuity before manufacture. The matching connector is Adafruit 5358, not
five-pin 5413. The drawing gives 14.2 mm magnet-center spacing; magnet geometry,
polarity and preload still require a mechanical mating test.
D6 isolates dock +5V from VBUS; U11 protects USB data and R29/R30 are 27 Ω.
Do not assume the wet data/ground contacts are electrically inert: measure
undocked leakage with the actual USB/ESD circuit. Charge only on a dry dock.

## Pin contract

| nRF pin | Net | Function |
|---|---|---|
| P0.26 / P0.27 | SDA / SCL | I2C: AS7341 0x39, FDC1004 0x50, MS5837 0x76, LSM6DSO 0x6A |
| P0.02 / P0.03 | EC_A / EC_B | Force electrode SAADC AIN0/AIN1 |
| P0.04 / P0.05 | EC_SENSE_A / EC_SENSE_B | Sense electrode SAADC AIN2/AIN3 |
| P0.22 / P0.23 | EC_DRV_LO / EC_DRV_HI | AC excitation through 1 kΩ / 100 kΩ; Hi-Z idle |
| P0.30 | EC_BIAS_EN | Switched R20 bias feed; low/Hi-Z idle |
| P0.13 / P0.14 / P0.15 | LED_WHITE / LED_850 / LED_365 | Q1 / Q2 / Q3 gates |
| P0.16 | OW_DQ | DS18B20U+ 1-wire |
| P0.17 | HEATER_EN | Q4 gate |
| P0.19 | PIEZO | Q5 gate |
| P0.20 | BOOST_EN | TPS61023 enable; R33 100 kΩ pulldown |
| P0.21 | IMU_INT | LSM6DSO INT1 |
| P0.08 / P0.06 | PDM_CLK / PDM_DATA | IM69D130 |
| P0.24 / P0.25 | UART_TX / UART_RX | Reserved debug labels; currently no connected test points |
| P0.07 | CHG_STAT | MCP73832 open-drain status; not dock-present detection |
| P0.12 | LED_STAT | D8 through R31, active-high |
| P1.00 | RING_DATA | R32 → 12 LED chain |
| P1.08 / P1.09 | BTN_DFU / BTN_FRESET | TP21 / TP22, ground to assert |
| P0.28 / P0.29 | EXP_A4 / EXP_A5 | TP23 / TP24 and E5 / E6; optional experiment only |
| P0.00 / P0.01 | EXP_00 / EXP_01 | TP25 / TP26; no external LF crystal |
| P0.09 / P0.10 | NFC1 / NFC2 | Optional external coil; retain NFC pin configuration |
| P0.18 | RESET | SWD/reset access; configure PSELRESET in bootloader |
| P0.11 / P0.31 | NC | No UVC circuit in spin 1 |
| USB D+ / D− | USB_DP / USB_DM | R30 / R29 → USBLC6-2SC6 → dock |
| VBUS | VBUS | Dock +5V through D6; USBREGSTATUS detects presence |
| VDDH / VDD | VBAT / 3V3 | Battery input / REG0 output; do not drive VDD externally in this mode |

## Sensors and excitation

- EC: E3/E4 force, E1/E2 sense. R3/R4 select 1 kΩ / 100 kΩ excitation;
  C1/C2 are 4.7 µF coupling capacitors. R20/R21 form the bias divider,
  C16 is 100 nF, R22/R23 and R26/R27 bias the force/sense inputs.
  **R20 is supplied by EC_BIAS_EN, not permanent 3V3.** Allow settling after
  enabling bias, then use balanced AC bursts. Disconnect both drive pins and
  disable bias between acquisitions and while docked. Validate net DC against
  the wet dock ground and pressure-sensor housing, not just across E3/E4.
- The high-impedance sense nodes require measured SAADC settling/loading checks.
  Sequential `analogRead` subtraction is not a four-wire synchronous instrument.
  Use timer/PPI-driven acquisition and record settings plus raw counts. P0.22/23
  are drive GPIOs, not ADC inputs for direct drive-voltage sampling.
- U4 FDC1004DGSR uses CIN1/CIN2 and SHLD1. FDC1 is a disc, FDC2 a concentric
  ring at the same height. They are experimental dielectric/wetness channels,
  not two points on a vertical level gradient. Log CAPDAC for every sample.
- U5 MS5837-02BA01-50 pressure: C10 is beside U5 on the sensor face. Preserve
  the gel port and provide a defined water seal around the package/PCB junction.
- U6 **DS18B20U+ µSOP**, U8 LSM6DSO, U9 IM69D130. R11 is a 100 Ω heater,
  about 0.25 W while enabled. U6 and R11 are separated in this layout; thermal
  flow/composition sensitivity must be demonstrated, not assumed.
- D1 **67-21/T2C-ZV1W2E/2T** white and D2 **HIR67-21C/L11/TR8** 850 nm use
  the project Everlight **non-ST** PLCC2 footprint (1.5 × 2.6 mm lands).
  KiCad pad 1 is cathode; vendor pin numbering is different. Review the body
  chamfer and placement rotation during assembly review.
- D3 **VLMU1610-365-135** uses its 1.6 × 1.6 mm package footprint; it is not a
  3528 substitute. R5/R6/R7 are 220/360/150 Ω. Optical gain/integration and
  excitation state must accompany raw spectral counts. A shroud and cured-resin
  optical test are required before sealing. Keep the ring dark during sensing.
- D10–D21 are XL-1010RGBC; C18–C23 bypass the ring, R32 is 220 Ω and D9 is
  its supply diode. Hold data low when the boost supply is off.
- NFC is optional: L2 is an external coil connection, C12/C13 **DNP pending
  measured tuning**. E5/E6 are experimental aux electrodes, not calibrated pH.

## Release requirements

Follow `../docs/validation-plan.md`: ERC/DRC and schematic parity, land-pattern
and 1:1 mating checks, assembly quote/rotation review, unsealed electrical and
wet testing, and failed-application recovery before any permanent dip. No
fabrication order or waterproof/performance claim is authorized by a rendered PCB.
The custom bootloader and sensing application remain unfinished.
