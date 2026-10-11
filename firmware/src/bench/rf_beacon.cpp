// The jug RF test — retires the project's #1 physics risk.
//
// Flash this, seal the XIAO + a LiPo in a zip bag (or epoxy blob with a dry
// air pocket under the antenna end), sink it in a glass jug, and walk around
// the room with nRF Connect on your phone watching RSSI. Log RSSI vs:
// distance, jug full/half/empty, antenna edge up vs down, phone above vs
// beside the jug. That table goes straight into the report.
#include <Arduino.h>
#include <bluefruit.h>

static uint32_t counter = 0;
static uint8_t mfg[6];  // 2-byte company id (0xFFFF test) + 4-byte counter

static void updateAdv() {
  mfg[0] = 0xFF; mfg[1] = 0xFF;
  memcpy(&mfg[2], &counter, 4);
  Bluefruit.Advertising.clearData();
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addManufacturerData(mfg, sizeof(mfg));
  Bluefruit.Advertising.addName();
}

void setup() {
  Serial.begin(115200);
  Bluefruit.begin();
  Bluefruit.setTxPower(0);  // match the carrier; repeat at +4 dBm as a separate run
  Bluefruit.setName("waterpuck-rf");
  updateAdv();
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(160, 160);  // 100 ms — fast, for RSSI sampling
  Bluefruit.Advertising.start(0);               // never stop
}

void loop() {
  // Counter in the payload proves packets are fresh, not cached by the phone.
  counter++;
  updateAdv();
  delay(1000);
}
