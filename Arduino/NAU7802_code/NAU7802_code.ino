#include <Adafruit_NAU7802.h>

Adafruit_NAU7802 nau;

void setup() {
  Serial.begin(115200);
  Serial.println("NAU7802");
  
  nau.begin();
  nau.setLDO(NAU7802_3V0);
  nau.setGain(NAU7802_GAIN_128);
  nau.setRate(NAU7802_RATE_10SPS);
  nau.calibrate(NAU7802_CALMOD_INTERNAL);
  nau.calibrate(NAU7802_CALMOD_OFFSET);
}

void loop() {

  int32_t val = nau.read();
  Serial.print("Read "); Serial.println(val);
}