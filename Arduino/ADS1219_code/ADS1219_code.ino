#include <Wire.h>
#include <ADS1219.h>
#define address 0x40
#define rst 2
#define drdy 3

ADS1219 ads(drdy);

void setup() {
  ads.begin();
  pinMode(drdy,INPUT_PULLUP);
  pinMode(rst,OUTPUT);
  digitalWrite(rst,HIGH);
  Wire.begin();
  Serial.begin(9600);
  ads.setVoltageReference(REF_EXTERNAL);
  ads.setConversionMode(MODE_CONTINUOUS);
}

void loop() {
  Serial.println("Single ended result:");
  Serial.println(ads.readSingleEnded(2)*5.096/pow(2,23),5);
  delay(500);
}
