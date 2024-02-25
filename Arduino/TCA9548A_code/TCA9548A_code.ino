#include <Arduino.h>
#include "TCA9548A.h"
#include "PCF8574.h"
#include <ADS1219.h>

TCA9548A I2CMux;                  // Address can be passed into the constructor

ADS1219 ads(P3);

void setup() {
  Serial.begin(9600);

  //  Wire.setPins(21, 22);       // ESP32 users, use setPins(sda, scl) if customised, *before* passing Wire to the library (the line below).  
  I2CMux.begin(Wire);             // Wire instance is passed to the library

  I2CMux.closeAll();              // Set a base state which we know (also the default state on power on)

  ads.begin();
  // pinMode(drdy,INPUT_PULLUP);
  // pinMode(rst,OUTPUT);
  // digitalWrite(rst,HIGH);
  // Wire.begin();
  Serial.begin(9600);
  ads.setVoltageReference(REF_EXTERNAL);
  ads.setConversionMode(MODE_CONTINUOUS);
}

void loop() 
{
  I2CMux.openChannel(7);
  Serial.println(ads.readSingleEnded(2)*4.96/pow(2,23),5);
  I2CMux.closeChannel(7);

  I2CMux.openChannel(1);
  I2CMux.openChannel(2);
  Serial.println(ads.readSingleEnded(2)*4.96/pow(2,23),5);
  I2CMux.closeAll();

  delay(1000);
}