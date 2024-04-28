#include <Adafruit_NAU7802.h>
#include "TCA9548A.h"

Adafruit_NAU7802 nau;
TCA9548A I2CMux;

TwoWire wire = Wire;
int nau_check[8]; 

void setup() {
  Serial.begin(9600);
  Serial.println("NAU7802");
  
  I2CMux.begin(Wire); 
  for(int i = 0; i < 8; i++){
    I2CMux.closeAll();              // Set a base state which we know (also the default state on power on)
    I2CMux.openChannel(i);
    if(nau.begin()){
      nau.setLDO(NAU7802_EXTERNAL);
      nau.setGain(NAU7802_GAIN_128);
      nau.setRate(NAU7802_RATE_10SPS);
      nau.calibrate(NAU7802_CALMOD_INTERNAL);
      nau.calibrate(NAU7802_CALMOD_OFFSET);
      nau_check[i] = 1;
    }
    delay(100);
  }
  // delay(2000);
}

void loop() {
  for(int i = 4; i < 8; i++){
    I2CMux.closeAll();              // Set a base state which we know (also the default state on power on)
    I2CMux.openChannel(i);

    if(nau_check[i] == 1){
      int32_t val = nau.read();
      Serial.print("Read ["); Serial.print(i+1); Serial.print("] "); Serial.print(val*(100)/4294620.0); Serial.print(" ");
    }
    else{
      Serial.print("Read ["); Serial.print(i+1); Serial.print("] "); Serial.print("NA"); Serial.print(" ");
    }
    delay(1000);
  }
  Serial.println("");
}
