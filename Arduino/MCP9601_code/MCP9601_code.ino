#include "Adafruit_MCP9601.h"
#include "TCA9548A.h"

#define I2C_ADDRESS (0x67)

Adafruit_MCP9601 mcp;

TCA9548A I2CMux; 

void setup()
{
  Serial.begin(115200);

  I2CMux.begin(Wire);             // Wire instance is passed to the library

  I2CMux.closeAll();              // Set a base state which we know (also the default 
  I2CMux.openChannel(2);              // Set a base state which we know (also the default state on power on)
  
  /* Initialise the driver with I2C_ADDRESS and the default I2C bus. */
  if(mcp.begin(I2C_ADDRESS)){
    mcp.setADCresolution(MCP9600_ADCRESOLUTION_12);

    mcp.setThermocoupleType(MCP9600_TYPE_K);
    mcp.setFilterCoefficient(0);
  }

  delay(1000);
}

void loop()
{
  uint8_t status = mcp.getStatus();
  Serial.print("MCP Status: 0x"); 
  Serial.print(status, HEX);  
  Serial.print(": ");
  if (status & MCP9601_STATUS_OPENCIRCUIT) { 
    Serial.println("Thermocouple open!"); 
    return; // don't continue, since there's no thermocouple
  }
  // if (status & MCP9601_STATUS_SHORTCIRCUIT) { 
  //   Serial.println("Thermocouple shorted to ground!"); 
  //   return; // don't continue, since the sensor is not working
  // }
  // if (status & MCP960X_STATUS_ALERT1) { Serial.print("Alert 1, "); }
  // if (status & MCP960X_STATUS_ALERT2) { Serial.print("Alert 2, "); }
  // if (status & MCP960X_STATUS_ALERT3) { Serial.print("Alert 3, "); }
  // if (status & MCP960X_STATUS_ALERT4) { Serial.print("Alert 4, "); }
  // Serial.println();
  
  // if(mcp.begin(I2C_ADDRESS)){
    Serial.println(mcp.readThermocouple());
  // }
  // else{
  //   Serial.println("NA");
  // }
  //Serial.print("Cold Junction: "); Serial.println(mcp.readAmbient());
  //Serial.print("ADC: "); Serial.print(mcp.readADC() * 2); Serial.println(" uV");

  delay(50);
}
