// EC front-end bring-up (protoboard stage — before the carrier exists).
// Wiring per hardware/carrier-board-spec.md:
//   D1 --1k--+          D2 --100k--+
//            +--[electrode A ... water ... electrode B]-- GND-side sense
//   D0 = ADC on electrode A node, D3 = ADC on electrode B node
// Bipolar excitation: alternate drive polarity so net DC across the
// electrodes is zero (no electrolysis, no polarization drift).
// Validate against the homemade KCl standard (0.7455 g/L = 1413 µS/cm @25°C).
#include <Arduino.h>

const uint8_t PIN_DRIVE_LO = 1;   // D1, 1k series — conductive liquids
const uint8_t PIN_DRIVE_HI = 2;   // D2, 100k series — near-pure water
const uint8_t PIN_SENSE_A = 0;    // D0 ADC
const uint8_t PIN_SENSE_B = 3;    // D3 ADC

// One bipolar measurement burst on the selected drive pin.
// Returns averaged |A-B| ADC delta over both polarities.
static float ecBurst(uint8_t drivePin, uint16_t cycles = 64) {
  pinMode(drivePin, OUTPUT);
  int32_t acc = 0;
  for (uint16_t i = 0; i < cycles; i++) {
    digitalWrite(drivePin, HIGH);
    delayMicroseconds(100);                    // ~5 kHz half-period
    int hi = analogRead(PIN_SENSE_A) - analogRead(PIN_SENSE_B);
    digitalWrite(drivePin, LOW);
    delayMicroseconds(100);
    int lo = analogRead(PIN_SENSE_A) - analogRead(PIN_SENSE_B);
    acc += hi - lo;                            // bipolar difference
  }
  pinMode(drivePin, INPUT);                    // high-Z between bursts: zero net DC
  return (float)acc / (2.0f * cycles);
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 5000) {}
  analogReadResolution(12);
  analogSampleTime(10);  // 10 us TACQ: default 3 us only rated to 10k source — high range is ~100k (design review M9)
  pinMode(PIN_DRIVE_LO, INPUT);
  pinMode(PIN_DRIVE_HI, INPUT);
  Serial.println("ec bring-up: raw bipolar deltas, both ranges");
  Serial.println("lo_range_raw,hi_range_raw");
}

void loop() {
  // Log RAW values only — calibration (cell constant, temp comp) is applied
  // downstream, per project rule #1.
  float lo = ecBurst(PIN_DRIVE_LO);
  float hi = ecBurst(PIN_DRIVE_HI);
  Serial.printf("%.2f,%.2f\n", lo, hi);
  delay(500);
}
