#include <Wire.h>
#include "PCF8574.h"
#include <ADS1219.h>
#define address 0x40
#define rst 2
#define drdy 3

ADS1219 ads(P3);

void setup() {
  ads.begin();
  // pinMode(drdy,INPUT_PULLUP);
  // pinMode(rst,OUTPUT);
  // digitalWrite(rst,HIGH);
  // Wire.begin();
  Serial.begin(9600);
  ads.setVoltageReference(REF_EXTERNAL);
  ads.setConversionMode(MODE_CONTINUOUS);
}

void loop() {
  Serial.println("Single ended result:");
  unsigned long startTime = micros();
  Serial.println(ads.readSingleEnded(2)*4.96/pow(2,23),5);
  unsigned long executionTime = micros() - startTime;
  Serial.print("Execution time: ");
  Serial.print(executionTime);
  Serial.println(" microseconds");
  delay(500);
}