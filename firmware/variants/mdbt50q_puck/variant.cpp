/*
  Sensei Puck carrier board variant — Raytac MDBT50Q-1MV2 (nRF52840).
  Identity pin map (Arduino N == P0.N, 32+N == P1.N), copied from the
  Adafruit BSP pca10056 variant. See variant.h for the net map and the
  USE_LFRC / no-DCDC / REGOUT0 commissioning notes.
*/

#include "variant.h"

#include "wiring_constants.h"
#include "wiring_digital.h"
#include "nrf.h"
#include "nrf_gpio.h"

const uint32_t g_ADigitalPinMap[] =
{
  // P0.00 .. P0.31
  0 , 1 , 2 , 3 , 4 , 5 , 6 , 7 ,
  8 , 9 , 10, 11, 12, 13, 14, 15,
  16, 17, 18, 19, 20, 21, 22, 23,
  24, 25, 26, 27, 28, 29, 30, 31,

  // P1.00 .. P1.15
  32, 33, 34, 35, 36, 37, 38, 39,
  40, 41, 42, 43, 44, 45, 46, 47
};

void initVariant()
{
  // Establish safe output latches BEFORE enabling the output drivers.
  const uint8_t off[] = {PIN_BOOST_EN, PIN_HEATER_EN, PIN_LED_WHITE,
    PIN_LED_850, PIN_LED_365, PIN_PIEZO, PIN_RING_DATA, PIN_EC_BIAS_EN, PIN_LED1};
  for (uint8_t pin : off) {
    nrf_gpio_pin_clear(pin);
    nrf_gpio_cfg_output(pin);
  }
  nrf_gpio_cfg_default(PIN_EC_DRV_LO);
  nrf_gpio_cfg_default(PIN_EC_DRV_HI);

  // initVariant runs before the scheduler and before Bluefruit.begin().
  // Program only an erased field; never erase UICR (would destroy NFC/reset
  // configuration), and never attempt an impossible flash 0->1 transition.
  const uint32_t old = NRF_UICR->REGOUT0;
  if ((old & UICR_REGOUT0_VOUT_Msk) == UICR_REGOUT0_VOUT_DEFAULT) {
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Wen;
    while (!NRF_NVMC->READY) {}
    NRF_UICR->REGOUT0 = (old & ~UICR_REGOUT0_VOUT_Msk) | UICR_REGOUT0_VOUT_3V3;
    while (!NRF_NVMC->READY) {}
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Ren;
    while (!NRF_NVMC->READY) {}
    __DSB(); __ISB();
    NVIC_SystemReset();
  }
  // DCDCEN0/DCCH and NFCPINS are deliberately untouched.
}
