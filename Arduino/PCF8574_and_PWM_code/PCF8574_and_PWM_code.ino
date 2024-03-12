#include "Arduino.h"
#include "PCF8574.h"

// Set the i2c HEX address
PCF8574 pcf8574(0x20);
PCF8574 pcf85741(0x21);

// pwm
const int PWM = 6; // D

void setup(){
  Serial.begin(9600);

  pinMode(PWM, OUTPUT);

  // Set the pinModes
  pcf8574.pinMode(P0, OUTPUT);
  pcf8574.pinMode(P1, OUTPUT);
  pcf8574.pinMode(P3, OUTPUT);
  pcf8574.pinMode(P2, INPUT);
  pcf8574.begin();
  pcf8574.digitalWrite(P3, HIGH);

  pcf85741.pinMode(P0, OUTPUT);
  pcf85741.pinMode(P1, OUTPUT);
  pcf85741.pinMode(P3, OUTPUT);
  pcf85741.begin();
}

void loop(){
  pcf8574.digitalWrite(P0, HIGH);
  pcf8574.digitalWrite(P1, LOW);
  Serial.print(pcf8574.digitalRead(P2));
  Serial.print("\n");
  analogWrite(PWM, 254);
  // delay(5000);
  Serial.println("hello1");
  pcf8574.digitalWrite(P0, LOW);
  pcf8574.digitalWrite(P1, HIGH);
  Serial.print(pcf8574.digitalRead(P2));
  Serial.print("\n");
  analogWrite(PWM, 50);
  // delay(5000);
  Serial.println("hello2");
}
