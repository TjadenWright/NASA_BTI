#include "Arduino.h"
#include "PCF8574.h"

// Set the i2c HEX address
PCF8574 pcf8574(0x20);

// pwm
const int PWM = 6; // D

void setup(){
  Serial.begin(9600);

  pinMode(PWM, OUTPUT);

  // Set the pinModes
  pcf8574.pinMode(P0, OUTPUT);
  pcf8574.pinMode(P1, OUTPUT);
  pcf8574.pinMode(P2, INPUT);
  pcf8574.begin();
}

void loop(){
  pcf8574.digitalWrite(P0, HIGH);
  pcf8574.digitalWrite(P1, LOW);
  Serial.print(pcf8574.digitalRead(P2));
  Serial.print("\n");
  analogWrite(PWM, 254);
  delay(5000);
  pcf8574.digitalWrite(P0, LOW);
  pcf8574.digitalWrite(P1, HIGH);
  Serial.print(pcf8574.digitalRead(P2));
  Serial.print("\n");
  analogWrite(PWM, 50);
  delay(5000);
}
