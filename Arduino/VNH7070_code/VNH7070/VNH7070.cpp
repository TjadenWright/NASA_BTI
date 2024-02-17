#if ARDUINO >= 100
 #include "Arduino.h"
#else
 #include "WProgram.h"
#endif

#include "VNH7070.h"
#include "PCF8574.h"

VNH7070::VNH7070(int PWM, int INA, int INB, int SEL0, uint8_t addr_expander) : pcf8574(addr_expander) {
  A = INA;
  B = INB;
  S = SEL0;
  PWM_OUT = PWM;
  pcf8574.pinMode(A, OUTPUT);
  pcf8574.pinMode(B, OUTPUT);
  pcf8574.pinMode(S, OUTPUT);
  pinMode(PWM_OUT, OUTPUT);
}

void VNH7070::begin() {
  pcf8574.begin();
  // start all off at zero
  stateA = 0;
  stateB = 0;
  stateOFF = 0;
}

void VNH7070::H_bridge_change(uint8_t PMW_value, int direction) {
  // if we are at B make sure to switch PWM to max and INB and INA to 0
  // INA = 0, INB = 1, SLE0 = 1, PWM = x
  if(direction > 0) {
    if(stateA == 0){
      analogWrite(PWM_OUT, 255);
      pcf8574.digitalWrite(B, LOW);
      pcf8574.digitalWrite(S, LOW);
      // now INA = 0, INB = 0, SLE0 = 0, PWM = 1  and still Hi-Z
      stateB = 0;
      pcf8574.digitalWrite(A, HIGH);
      stateA = 1;
    }
  }

  // if we are at A make sure to switch PWM to max and INB and INA to 0
  // INA = 1, INB = 0, SLE0 = 0, PWM = x
  else if(direction < 0){
    if(stateB == 0){
      analogWrite(PWM_OUT, 255);
      pcf8574.digitalWrite(A, LOW);
      pcf8574.digitalWrite(S, HIGH);
      // now INA = 0, INB = 0, SLE0 = 1, PWM = 1  and still Hi-Z
      stateA = 0;
      pcf8574.digitalWrite(B, HIGH);
      stateB = 1;
    }
  }
  // set analog value
  analogWrite(PWM_OUT, PMW_value);
}