#ifndef VNH7070_H
#define VNH7070_H

#if (ARDUINO >=100)
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif

#include "PCF8574.h"

class VNH7070  {
  protected:
	uint8_t address;
  public:
    // Constructor 
    VNH7070(uint8_t addr_expander = 0x20, uint8_t INA = P6, uint8_t INB = P5, uint8_t SEL0 = P7);

    // Methods
    void begin();
	void H_bridge_change(uint8_t PWM_OUT, uint8_t PMW_value, int8_t direction, bool & stateA, bool & stateB);

  private:
	uint8_t A, B, S;
	// int stateA, stateB, stateOFF;
	PCF8574 pcf8574;
};
#endif
