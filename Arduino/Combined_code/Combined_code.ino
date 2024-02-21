#include <Arduino.h>
#include <Wire.h>
#include "PCF8574.h" // controlling the I2C gpio expander
#include <TMP1075.h> // reading I2C temeperature sensor
#include "VNH7070.h" // controlling H-Bridge
#include <ADS1219.h>

////////////////////
// GPIO Expanders //
////////////////////
PCF8574 pcf8574_first(0x20);
PCF8574 pcf8574_second(0x21);

////////////////////////////
// I2C temperature sensor //
////////////////////////////
TwoWire wire = Wire;
TMP1075::TMP1075 tmp1075 = TMP1075::TMP1075(wire);    // The library uses the namespace TMP1075

//////////////
// H-bridge //
//////////////
VNH7070 vnh(6);

/////////////
// I2C ADC //
/////////////
ADS1219 ads(P3);


void setup() {
    // put your setup code here, to run once:
    Serial.begin(9600);

    ////////////////////
    // GPIO Expanders //
    ////////////////////
    // Set the pinModes for left expander in schematic
    pcf8574_first.pinMode(P0, OUTPUT); // Forward/Reverse
    pcf8574_first.pinMode(P1, OUTPUT); // Motor Enable? (ASK!!) <-----------------
    pcf8574_first.pinMode(P2, OUTPUT); // Brake
    // PIN3 is being used in ADC for DRDY (already setup in the function)
    pcf8574_first.pinMode(P4, INPUT); // Alarm from Motor
    // PIN5-7 are already used in the VNH7070 function
    pcf8574_first.begin();

    // Set the pinModes for right expander in schematic
    pcf8574_second.pinMode(P0, OUTPUT); // Enable Efuse
    pcf8574_second.pinMode(P1, INPUT); // Over current fault
    pcf8574_second.pinMode(P2, INPUT); // Over "T" Alert <---------------- (threashold)?
    pcf8574_second.pinMode(P6, OUTPUT); // RESET something??? <----------------- (ASK!!)
    // Reset of the pins are not used
    pcf8574_second.begin();

    ////////////////////////////
    // I2C temperature sensor //
    ////////////////////////////
    wire.begin(0x48);  // See definition of wire above
    tmp1075.begin();  // Syncs the config register

    //////////////
    // H-bridge //
    //////////////
    vnh.begin();

    /////////////
    // I2C ADC //
    /////////////
    ads.begin();
    // Set some stuff for ADC
    ads.setVoltageReference(REF_EXTERNAL);
    ads.setConversionMode(MODE_CONTINUOUS);
    // A1 feedback, A2 SPEED, A3 Current
}

void loop() {
    // Fun communication! (first test all functions at once then communicate with python)
}
