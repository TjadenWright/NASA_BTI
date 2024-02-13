#include <Arduino.h>
#include "DS3930.h"

DS3930 digiPotDS(0x50);

int i = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  digiPotDS.begin();
  
  delay(10);

  // First wiper
  digiPotDS.setPotNumb(0);
  digiPotDS.writeWiper(200);                 // Baseline Establish

  delay(10);

  Serial.println("\n----- Wiper Register0 ----");
  Serial.print("readWiper0: ");
  Serial.println(digiPotDS.readWiper());

  delay(1);

// fourth wiper
  digiPotDS.setPotNumb(3);
  digiPotDS.writeWiper(200);                 // Baseline Establish

  delay(1);

  Serial.println("\n----- Wiper Register3 ----");
  Serial.print("readWiper3: ");
  Serial.println(digiPotDS.readWiper());

  delay(1);

}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("....... Functionality Test Begin ..........");
  /* Wiper ........................... */

  if(i < 256)
    i=i+20;
  else
    i = 0;

  // first wiper
  digiPotDS.setPotNumb(0);
  Serial.println("\n----- Wiper Register0 ----");
  Serial.print("readWiper0: ");
  Serial.println(digiPotDS.readWiper());

  delay(1);

  digiPotDS.setPotNumb(3);

  delay(1);

  Serial.println("\n----- Wiper Register3 ----");
  Serial.print("readWiper3: ");
  Serial.println(digiPotDS.readWiper());

// second wiper
  digiPotDS.setPotNumb(1);
  digiPotDS.writeWiper(i);                 // Baseline Establish

  delay(1);

  Serial.println("\n----- Wiper Register1 ----");
  Serial.print("readWiper1: ");
  Serial.println(digiPotDS.readWiper());

  delay(1);

// third wiper
  digiPotDS.setPotNumb(2);
  digiPotDS.writeWiper(i);                 // Baseline Establish

  delay(1);

  Serial.println("\n----- Wiper Register2 ----");
  Serial.print("readWiper2: ");
  Serial.println(digiPotDS.readWiper());

  delay(1);

  digiPotDS.writeIO(0x00);

  delay(1);

  Serial.println("\n----- IO Register ----");
  Serial.print("readWiper: ");
  Serial.println(digiPotDS.readIO(), HEX);

  delay(1);

  digiPotDS.writeIO(0x1F);

  delay(1);

  Serial.println("\n----- IO Register ----");
  Serial.print("readWiper: ");
  Serial.println(digiPotDS.readIO(), HEX);

  delay(1000);
}
