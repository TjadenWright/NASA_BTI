#include "Arduino.h"
#include "VNH7070.h"

// Set the i2c HEX address
VNH7070 vnh(0x20);

void setup(){
  Serial.begin(9600);
  vnh.begin();
}

int i = 255;

void loop(){
  vnh.H_bridge_change(i, 1);
  Serial.print("Forward ");
  Serial.println(i*16.0/255);
  delay(5000);
  vnh.H_bridge_change(i, -1);
  Serial.print("Backward ");
  Serial.println(i*16.0/255);
  delay(5000);

  if(i >= 50){
    i = i - 50;
  }
  else
    i = 255;
}
