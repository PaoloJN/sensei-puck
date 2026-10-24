/*
  Water Puck carrier board variant — Raytac MDBT50Q-1MV2 (nRF52840, bare module).

  Based on the Adafruit nRF52 BSP `pca10056` variant (nRF52840-DK), which uses
  the full 48-pin identity map — the standard bare-module convention:

      Arduino pin N  ==  P0.N   for N in 0..31
      Arduino pin 32+N == P1.N  for N in 0..15

  So the macros below can be read straight off the schematic: pin 26 is P0.26,
  pin 41 is P1.09, etc.

  Pin map source of truth: hardware/carrier-board-spec.md ("Pin map" section).
  Update BOTH files together when nets move.

  ---------------------------------------------------------------------------
  SAFETY / COMMISSIONING NOTES (carrier-board-spec.md, review items C2 etc.)
  ---------------------------------------------------------------------------
  1. LF clock: **USE_LFRC only.** The MDBT50Q-1MV2 has NO 32.768 kHz crystal.
     Never copy USE_LFXO from the XIAO (or pca10056/raytac_rx) variants — the
     SoftDevice hangs at boot waiting for a crystal that isn't there.
     LFRC frees P0.00/P0.01 (XL1/XL2) as spare GPIO.

  2. DC/DC: the module's DCCH pad is UNCONNECTED (no LC fitted). Firmware must
     NEVER set DCDCEN/DCDCEN0 (NRF_POWER->DCDCEN[0]) — enabling it soft-bricks
     the board including debug access. This variant defines no DCDC-related
     macro and initVariant() touches no POWER registers. Keep it that way.

  3. UICR REGOUT0 = 3V3 dependency: we run VDDH mode (battery -> VDDH), so the
     "3V3" rail is REG0's *output* and the erased UICR default is 1.8 V. A
     blank/erased module boots BLE but starves FDC1004/DS18B20 and the FET
     gates. Commissioning flashes REGOUT0=3V3 over SWD
     (`nrfjprog --memwr 0x10001304 --val 5` + reset, then measure 3.3 V).
     initVariant() implements an erased-field-only guard: NVMC write VOUT=3V3,
     preserve reserved bits, then reset. A non-default wrong setting is not
     rewritten; the commissioning image reports STOP_CHECK_3V3. Measure the
     actual rail before enabling sensors. This does not replace SWD recovery.

  4. NFC pins P0.09/P0.10: NFC-A coil. Never CONFIG_NFCT_PINS_AS_GPIOS, never
     use them as GPIO. Bootloader build must keep USE_NFCT = yes.

  5. RESET is P0.18 via CONFIG_GPIO_AS_PINRESET (SWD pad set on the board).
*/

#ifndef _VARIANT_MDBT50Q_PUCK_
#define _VARIANT_MDBT50Q_PUCK_

/** Master clock frequency */
#define VARIANT_MCK       (64000000ul)

#define USE_LFRC    // NO 32 kHz crystal on the MDBT50Q-1MV2 — never USE_LFXO

/*----------------------------------------------------------------------------
 *        Headers
 *----------------------------------------------------------------------------*/

#include "WVariant.h"

#ifdef __cplusplus
extern "C"
{
#endif // __cplusplus

// Number of pins defined in PinDescription array (identity map, P0.00..P1.15)
#define PINS_COUNT           (48)
#define NUM_DIGITAL_PINS     (48)
#define NUM_ANALOG_INPUTS    (8)
#define NUM_ANALOG_OUTPUTS   (0)

/*
 * LEDs — P0.12 is now a REAL status LED (schematic Block 10b, 2026-08-31):
 * D8 0603 + R31 1 k to GND, net LED_STAT, active high. The placeholder became
 * hardware, so LED_BUILTIN/ledOn/Bluefruit conn-LED blink for real. (D1-D3
 * remain illumination loads behind FET gates on the boost rail — not
 * indicators, and invisible to the bootloader while the rail is down.)
 *
 * Bootloader buttons — picked 2026-08-31 (was "revisit at bootloader-pick
 * time"): BUTTON_DFU = P1.08 (TP21), BUTTON_FRESET = P1.09 (TP22). Bare
 * exposed pads, tweezer-to-GND with internal pull-ups; both pass the
 * button-pin blacklist (not IMU_INT, not PDM, not externally driven). The
 * bootloader board.h must use these same numbers.
 */
#define PIN_LED1             (8)    // P0.08 (module pad 24) — D8 status LED, net LED_STAT; moved from P0.12 (2026-10-16 pass 2)
#define LED_BUILTIN          PIN_LED1
#define LED_CONN             PIN_LED1
#define LED_RED              PIN_LED1
#define LED_BLUE             PIN_LED1
#define LED_STATE_ON         (1)    // active high (drives D8 through R31)

#define PIN_BTN_DFU          (1)   // P0.01 (module pad 18) — TP21, tweezer-to-GND forces DFU; pass 3
#define PIN_BTN_FRESET       (47)   // P1.15 (module pad 8) — TP22, factory-reset button pad; moved from P1.09 for routing (2026-10-16)

// Expansion pads (bottom east rim, 2026-09-04): spare pins on 4 SMD pads. 3V3/GND on the SWD row.
#define PIN_EXP_A4      (28)   // P0.28 / AIN4 — TP23 (v2 pH probe candidate)
#define PIN_EXP_A5      (29)   // P0.29 / AIN5 — TP24
#define PIN_EXP_00           (4)   // P0.04 (module pad 20) — TP25; pass 3
#define PIN_EXP_01           (6)   // P0.06 (module pad 22) — TP26; pass 3

/*
 * Analog pins — SAADC channel order (AIN0..AIN7)
 */
#define PIN_A0               (2)    // P0.02 AIN0 = EC_A
#define PIN_A1               (3)    // P0.03 AIN1 = EC_B
#define PIN_A2               (4)    // P0.04 AIN2 = EXP_00 (digital) since the 2026-10-16 pin passes
#define PIN_A3               (5)    // P0.05 AIN3 = EC_SENSE_B
#define PIN_A4               (28)   // P0.28 AIN4 — EXP_A4 pad TP23 (spare, freed by EC-drive move)
#define PIN_A5               (29)   // P0.29 AIN5 — spare (freed by EC-drive move)
#define PIN_A6               (30)   // P0.30 AIN6 — EC_BIAS_EN (slow GPIO)
#define PIN_A7               (31)   // P0.31 AIN7 = EC_SENSE_A (since the 2026-10-16 pin swap)

static const uint8_t A0  = PIN_A0 ;
static const uint8_t A1  = PIN_A1 ;
static const uint8_t A2  = PIN_A2 ;
static const uint8_t A3  = PIN_A3 ;
static const uint8_t A4  = PIN_A4 ;
static const uint8_t A5  = PIN_A5 ;
static const uint8_t A6  = PIN_A6 ;
static const uint8_t A7  = PIN_A7 ;
#define ADC_RESOLUTION    14

/*
 * Serial interfaces — debug UART on test points only
 */
#define PIN_SERIAL1_RX       (25)   // P0.25 UART_RX
#define PIN_SERIAL1_TX       (34)   // P1.02 (module pad 50) UART_TX, reserved label; pin pass 4 (2026-10-17), was P0.24

/*
 * SPI Interfaces — NO SPI bus on the puck (everything is I2C/PDM/1-wire).
 * Macros exist only so the core SPI library (pulled in via Adafruit BusIO)
 * compiles; they point at spare P1.xx pins and nothing initializes them.
 */
#define SPI_INTERFACES_COUNT 1

#define PIN_SPI_MISO         (40)   // P1.08 — spare, macro-only
#define PIN_SPI_MOSI         (41)   // P1.09 — spare, macro-only
#define PIN_SPI_SCK          (32)   // P1.00 — spare, macro-only

static const uint8_t SS   = (33);   // P1.01 — spare, macro-only
static const uint8_t MOSI = PIN_SPI_MOSI ;
static const uint8_t MISO = PIN_SPI_MISO ;
static const uint8_t SCK  = PIN_SPI_SCK ;

/*
 * Wire Interfaces — AS7341 0x39, FDC1004 0x50, LSM6DSO 0x6A, MS5837 0x76
 */
#define WIRE_INTERFACES_COUNT 1

#define PIN_WIRE_SDA         (0)   // P0.00 (module pad 17); third assignment pass 2026-10-16, escape plan
#define PIN_WIRE_SCL         (27)   // P0.27

#define PIN_SDA              PIN_WIRE_SDA
#define PIN_SCL              PIN_WIRE_SCL

/*----------------------------------------------------------------------------
 *  Puck net map (hardware/carrier-board-spec.md "Pin map")
 *----------------------------------------------------------------------------*/

// EC front end — 4-electrode cell
#define PIN_EC_A             (2)    // P0.02 AIN0 — force node E3 (2-el. fallback)
#define PIN_EC_B             (3)    // P0.03 AIN1 — force node E4 (2-el. fallback)
#define PIN_EC_SENSE_A       (31)   // P0.31 AIN7 (module pad 12) — inner sense electrode E1 (4-wire); moved from P0.04 for routing (2026-10-16)
#define PIN_EC_SENSE_B       (5)    // P0.05 AIN3 — inner sense electrode E2 (4-wire)
#define PIN_EC_DRV_LO        (22)   // P0.22 — 1 kOhm range drive (H0H1 high-drive)
#define PIN_EC_DRV_HI        (23)   // P0.23 — 100 kOhm range drive (H0H1 high-drive)
#define PIN_EC_BIAS_EN       (30)   // P0.30 — R20 divider feed; LOW between acquisitions
#define PIN_RING_DATA       (32)   // P1.00 — XL-1010 ring; LOW while boost is off

// Illumination FET gates (loads on 5 V boost rail)
#define PIN_LED_WHITE        (15)   // P0.15 (module pad 39) — Q1 gate; pin pass 4 (2026-10-17), was P0.13
#define PIN_LED_850          (13)   // P0.13 (module pad 37) — Q2 gate (850 nm scatter turbidity); pin pass 4 (2026-10-17), was P1.02
#define PIN_LED_365          (24)   // P0.24 (module pad 48) — Q3 gate (365 nm); pin pass 4 (2026-10-17), was P0.15

// Misc peripherals
#define PIN_OW_DQ            (42)   // P1.10 (module pad 3) — DS18B20U+ 1-wire; moved from P0.16 (2026-10-16 pass 2)
#define PIN_HEATER_EN        (17)   // P0.17 — Q4 gate
#define PIN_PIEZO            (19)   // P0.19 — Q5 gate (low-side FET, load off GPIO)
#define PIN_BOOST_EN         (20)   // P0.20 — TPS61023 EN
#define PIN_IMU_INT          (21)   // P0.21 — LSM6DSO INT1 (tilt wake)
#define PIN_CHG_STAT         (41)   // P1.09 (module pad 26) — MCP73832 STAT; pass 3

// PDM microphone (IM69D130) — names the core PDM library expects, plus the
// spec's PIN_PDM_DATA alias
#define PIN_PDM_CLK          (45)   // P1.13 (module pad 6); moved from P0.08 for routing (2026-10-16)
#define PIN_PDM_DATA         (43)   // P1.11 (module pad 4); moved from P0.06 for routing (2026-10-16)
#define PIN_PDM_DIN          PIN_PDM_DATA
#define PIN_PDM_PWR          (-1)   // mic powered from rail, no power gate

// Debug UART aliases (test points only; wired into Serial1 above)
#define PIN_UART_TX          PIN_SERIAL1_TX  // P0.24
#define PIN_UART_RX          PIN_SERIAL1_RX  // P0.25

// UVC organics channel — DNP footprints, populate at v2
#define PIN_UVC_EN           (11)   // P0.11 — 275 nm UVC LED drive (D7, DNP v2)
#define PIN_UVC_PD           (31)   // P0.31 AIN7 — GUVC-T21GH Vout (DNP v2)

// NFC coil — RESERVED. P0.09/P0.10 drive the etched NFC-A spiral. NEVER use
// as GPIO, never CONFIG_NFCT_PINS_AS_GPIOS (bootloader keeps USE_NFCT = yes).
#define PIN_NFC1             (9)    // P0.09 — NFC coil, never GPIO
#define PIN_NFC2             (10)   // P0.10 — NFC coil, never GPIO

#ifdef __cplusplus
}
#endif

/*----------------------------------------------------------------------------
 *        Arduino objects - C++ only
 *----------------------------------------------------------------------------*/

#endif // _VARIANT_MDBT50Q_PUCK_
