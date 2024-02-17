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
    VNH7070(int PWM = 6, int INA = P6, int INB = P5, int SEL0 = P7, uint8_t addr_expander = 0x20);

    // Methods
    void begin();
	void H_bridge_change(uint8_t PMW_value, int direction);

  private:
	int A, B, S, PWM_OUT;
	int stateA, stateB, stateOFF;
	PCF8574 pcf8574;
};
#endif
