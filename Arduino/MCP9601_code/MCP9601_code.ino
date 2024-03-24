#include "Adafruit_MCP9601.h"

#define I2C_ADDRESS (0x67)

Adafruit_MCP9601 mcp;

void setup()
{
  Serial.begin(115200);
  
  /* Initialise the driver with I2C_ADDRESS and the default I2C bus. */
  if(mcp.begin(I2C_ADDRESS)){
    mcp.setADCresolution(MCP9600_ADCRESOLUTION_18);

    mcp.setThermocoupleType(MCP9600_TYPE_K);
    mcp.setFilterCoefficient(7);
  }

  delay(1000);
}

void loop()
{
  // uint8_t status = mcp.getStatus();
  // Serial.print("MCP Status: 0x"); 
  // Serial.print(status, HEX);  
  // Serial.print(": ");
  // if (status & MCP9601_STATUS_OPENCIRCUIT) { 
  //   Serial.println("Thermocouple open!"); 
  //   return; // don't continue, since there's no thermocouple
  // }
  // if (status & MCP9601_STATUS_SHORTCIRCUIT) { 
  //   Serial.println("Thermocouple shorted to ground!"); 
  //   return; // don't continue, since the sensor is not working
  // }
  // if (status & MCP960X_STATUS_ALERT1) { Serial.print("Alert 1, "); }
  // if (status & MCP960X_STATUS_ALERT2) { Serial.print("Alert 2, "); }
  // if (status & MCP960X_STATUS_ALERT3) { Serial.print("Alert 3, "); }
  // if (status & MCP960X_STATUS_ALERT4) { Serial.print("Alert 4, "); }
  // Serial.println();
  
  if(mcp.begin(I2C_ADDRESS)){
    Serial.println(mcp.readThermocouple());
  }
  else{
    Serial.println("NA");
  }
  //Serial.print("Cold Junction: "); Serial.println(mcp.readAmbient());
  //Serial.print("ADC: "); Serial.print(mcp.readADC() * 2); Serial.println(" uV");

  // delay(1000);
}
