/****************************************************** 
  Arduino library for DS3930 digital potentiometers
  
  Author: Jonathan Dempsey JDWifWaf@gmail.com
  Edited: Tjaden Wright
  
  Version: 1.0.2
  License: Apache 2.0
 *******************************************************/

#include "DS3930.h"

#define DEBUG 0

/* 7 Bit I2C Operation Components ......................................... */

#define POT0   0xF0 // 0xF0 1111_0000
#define POT1   0xF1 // 0xF1 1111_0001
#define POT2   0xF2 // 0xF2 1111_0010
#define POT3   0xF3 // 0xF3 1111_0011
#define POT4   0xF4 // 0xF4 1111_0100
#define POT5   0xF5 // 0xF5 1111_0101

#define IO     0xF6 // 0xF6 1111_0110

#define ReadIO 0xF7 // 0xF6 1111_0111

// global variable
uint8_t ADD = POT0;

/* Setup ............................................................... */
DS3930::DS3930(uint8_t ReverseAddress) : _address(ReverseAddress) {};
 
void DS3930::begin(TwoWire &inWire)
{
    MCPWire = &inWire;
    this->MCPWire->begin();
    this->MCPWire->setClock(MCPCSPEED); 
}

void DS3930::setPotNumb(uint8_t POT_VALUE)
{
    // pot value
    if(POT_VALUE == 0)
        ADD = POT0;
    else if(POT_VALUE == 1)
        ADD = POT1;
    else if(POT_VALUE == 2)
        ADD = POT2;
    else if(POT_VALUE == 3)
        ADD = POT3;
    else if(POT_VALUE == 4)
        ADD = POT4;
    else if(POT_VALUE == 5)
        ADD = POT5;
}

/* Wiper Register..........................................................*/
void DS3930::writeWiper(uint8_t wiperValue)
{
    // potentiometer write
    this->MCPWire->beginTransmission(_address);
    this->MCPWire->write(ADD);
    this->MCPWire->write(wiperValue);
    this->MCPWire->endTransmission();
} 

// /* Currently doesn't work ................................................*/
uint8_t DS3930::readWiper()
{
    uint8_t buff = 0;
    // potentiometer write
    this->MCPWire->beginTransmission(_address);
    this->MCPWire->write(ADD);
    this->MCPWire->endTransmission(false);

    this->MCPWire->requestFrom(_address, (uint8_t)2);
    // get data
    buff = this->MCPWire->read();   // First byte is 0x00
    #if DEBUG
    Serial.print("\nRead Wiper MSB:  ");
    Serial.println(buff);
    #endif

    return buff;
} 

void DS3930::writeIO(uint8_t writeValue)
{
    // potentiometer write
    this->MCPWire->beginTransmission(_address);
    this->MCPWire->write(IO);
    this->MCPWire->write(writeValue);
    this->MCPWire->endTransmission();
} 

// /* Currently doesn't work ................................................*/
uint8_t DS3930::readIO()
{
    uint8_t buff = 0;
    // potentiometer write
    this->MCPWire->beginTransmission(_address);
    this->MCPWire->write(ReadIO);
    this->MCPWire->endTransmission(false);

    this->MCPWire->requestFrom(_address, (uint8_t)2);
    // get data
    buff = this->MCPWire->read();   // First byte is 0x00
    #if DEBUG
    Serial.print("\nRead Wiper MSB:  ");
    Serial.println(buff);
    #endif

    return buff;
} 