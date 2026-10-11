// Bench milestone A, step 0: find everything on the bus.
// Expected with all breakouts wired: 0x39 (AS7341), 0x50 (FDC1004), 0x76 (MS5837).
#include <Arduino.h>
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 5000) {}
  Wire.begin();
  Serial.println("water-puck i2c scan");
}

void loop() {
  uint8_t found = 0;
  for (uint8_t addr = 0x08; addr < 0x78; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf("  device at 0x%02X\n", addr);
      found++;
    }
  }
  Serial.printf("scan done, %u device(s)\n\n", found);
  delay(2000);
}
