// Safe commissioning image. This is not the sensing/logging application.
#include <Arduino.h>
#include <nrf.h>

static bool supplyConfigured() {
#ifdef ARDUINO_MDBT50Q_PUCK
  return (NRF_UICR->REGOUT0 & UICR_REGOUT0_VOUT_Msk) == UICR_REGOUT0_VOUT_3V3;
#else
  return true;
#endif
}

static bool dockPowered() {
  // MCP73832 STAT is high-Z both when full and when unplugged. VBUS is the
  // source of truth; never restart measurements simply because STAT rises.
  return (NRF_POWER->USBREGSTATUS & POWER_USBREGSTATUS_VBUSDETECT_Msk) != 0;
}

void setup() {
  Serial.begin(115200);
  Serial.println("water-puck: commissioning idle; loads and EC bias disabled");
}

void loop() {
  static uint32_t lastReport = 0;
  if (Serial && millis()-lastReport >= 5000) {
    lastReport = millis();
    Serial.printf("uptime_ms=%lu,regout0=%08lx,dock=%u,state=%s\n",
      static_cast<unsigned long>(lastReport),
      static_cast<unsigned long>(NRF_UICR->REGOUT0), dockPowered(),
      supplyConfigured() ? "IDLE" : "STOP_CHECK_3V3");
  }
  // No radio, heater, optical loads or EC excitation in this commissioning
  // image. USB diagnostic overhead means charge termination must still be
  // bench-measured; this is not a claim of measured low-power operation.
  delay(1000);
}
