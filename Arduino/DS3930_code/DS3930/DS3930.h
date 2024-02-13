/****************************************************** 
  Arduino library for DS3930 digital potentiometers
  
  Author: Jonathan Dempsey JDWifWaf@gmail.com
  Edited: Tjaden Wright

  Version: 1.0.2
  License: Apache 2.0
 *******************************************************/

#ifndef _DS3930_H
#define _DS3930_H

#include <Arduino.h>
#include <Wire.h>

#define MCPCSPEED 100000     // I2C clock speed

class DS3930
{
    public:
 
        /* Setup ............................................................... */
        DS3930(uint8_t ReverseAddress = 0x50);

        void begin(TwoWire &inWire = Wire);

        /* Wiper Register ...................................................... */
        void setPotNumb(uint8_t POT_VALUE = 0);
        uint8_t readWiper();
        void writeWiper(uint8_t wiperValue);

        /* IO Register ......................................................... */
        void writeIO(uint8_t writeValue);
        uint8_t readIO();

    protected:
    private:
        uint8_t _address;

        TwoWire* MCPWire;
};

#endif