// need to invert alarm pin
  // may need to invert outputs (need to test on motor/actuator board)

#include <Arduino.h>
#include <Wire.h>
#include "PCF8574.h" // controlling the I2C gpio expander
#include <TMP1075.h> // reading I2C temeperature sensor
#include "VNH7070.h" // controlling H-Bridge
#include <ADS1219.h>
#include "TCA9548A.h"
#include <Adafruit_NAU7802.h>
#include "Adafruit_MCP9601.h"

#define TestArduinoScript false
#define Arduino_or_latte false // true -> arduino mega / false -> latte

#define MAX_SPEED 4.96
#define MAX_CURRENT 5000*(1/22.2) // 22.2 mV/A or 0.045 A/mV 
#define MAX_FEEDBACK 4.96

String commands[] = {"startup", "cMotor", "cActuator", "sMotorCurrent", "dMotor", "sMotrSpeed", "dMotrSpeed", "sActuatorCurrent", "dActuator", "sActuatrFeeback", "dActuatrFeeback", "dMotherboard", "dTempAndLC", "dIMU"}; 

// Commands
// startup LOW_HIGH
// cMotor Channel# EN EN_EFUSE PWM FR BRAKE 
// cActuator Channel# EN_EFUSE FR PWM
// sMotorCurrent Channel#                (starts the current conversion)
// dMotor Channel#                       you get this: ALARM TEMP CURRENT OC_FAULT
// sMotrSpeed Channel#                   (starts the speed conversion)
// dMotrSpeed Channel#                   you get this: SPEED
// sActuatorCurrent Channel#             (starts the current conversion)
// dActuator Channel#                    you get this: TEMP CURRENT OC_FAULT
// sActuatrFeeback Channel#              (starts the feedback conversion)
// dActuatrFeeback Channel# FEEBACK      you get this: FEEDBACK     
// dMotherboard Channel#                 you get this: ALARM TEMP CURRENT OC_FAULT
// dTempAndLC Channel#                   you get this: LC, TEMP_OUT
// dIMU Channel#                         you get this: _, _, ...

// check values
const uint8_t max_channels = 8; // for commands channel# doesn't count
const uint8_t max_input_outputs = 6;

// PWM channel pins
uint8_t Mega[max_channels] = {12, 6, 10, 11, 8, 9, 7, 13}; // 12, 13, 10, 11, 8, 9, 7, 6
// Mega reset = 5
uint8_t Panda[max_channels] = {13, 12, 11, 10, 9, 8, 7, 254}; // (negative one is a place holder)
// Panda reset = 4

uint8_t PWM_Channel[max_channels];
uint8_t Channel_Offset = 1;   // either 1 for 1-8 or 9 for 9-16
int8_t Channel_Selected = -1; // start with a channel we can't be in

bool stateA[max_channels] = {0, 0, 0, 0, 0, 0, 0, 0};
bool stateB[max_channels] = {0, 0, 0, 0, 0, 0, 0, 0};

// values stored (so we don't send multiple times the same thing)
int16_t vals[max_channels][6];

////////////////////
// GPIO Expanders //
////////////////////
PCF8574 pcf8574_Controls20(0x20);
PCF8574 pcf8574_Controls21(0x21);

////////////////////////////
// I2C temperature sensor //
////////////////////////////
TwoWire wire = Wire;
TMP1075::TMP1075 tmp1075 = TMP1075::TMP1075(wire);    // The library uses the namespace TMP1075

//////////////
// H-bridge //
//////////////
VNH7070 vnh(0x20);

/////////////
// I2C ADC //
/////////////
ADS1219 ads(P3);

/////////////
// I2C MUX //
/////////////
TCA9548A I2CMux;                  // Address can be passed into the constructor

///////////////
// LOAD CELL //
///////////////
Adafruit_NAU7802 nau;
// load cell check to see if its on the channel (hangs if you try to initialize it and its not on the channel)
bool nau_check[max_channels] = {0, 0, 0, 0, 0, 0, 0, 0}; 

//////////////////
// Thermocouple //
//////////////////
Adafruit_MCP9601 mcp;
// thermocouple check to see if its on the channel (hangs if you try to initialize it and its not on the channel)
bool mcp_check[max_channels] = {0, 0, 0, 0, 0, 0, 0, 0}; 

////////////////
// 1. I2C IMU //
////////////////


void setup() {
    // put your setup code here, to run once:
    if(Arduino_or_latte){
      Serial.begin(115200);
    }
    else{
      Serial.begin(9600);
    }

    // wait for Serial.print to start
    delay(2000);

    // setup vals array
    for(uint8_t i = 0; i < max_channels; i++)
      for(uint8_t j = 0; j < max_input_outputs; j++)
        vals[i][j] = -1;

    if(TestArduinoScript)
      Serial.println("reset");
    /////////
    // PWM //
    /////////
    // initialized in startup

    /////////////
    // I2C MUX //
    /////////////
    I2CMux.begin(Wire);             // Wire instance is passed to the library
  
    for(uint8_t i = 0; i < max_channels; i++){
      I2CMux.closeAll();              // Set a base state which we know (also the default state on power on)
      I2CMux.openChannel(i);
      ////////////////////
      // GPIO Expanders //
      ////////////////////
      if(i != max_channels - 1 || Arduino_or_latte){ // motor/actuator only on arduino
        // Set the pinModes for left expander in schematic
        pcf8574_Controls20.pinMode(P0, OUTPUT); // Forward/Reverse
        pcf8574_Controls20.pinMode(P1, OUTPUT); // Motor Enable
        pcf8574_Controls20.pinMode(P2, OUTPUT); // Brake
        // PIN3 is being used in ADC for DRDY (already setup in the function)
        pcf8574_Controls20.pinMode(P4, INPUT); // Alarm from Motor
        // PIN5-7 are already used in the VNH7070 function
      }
      else{ //motherboard
        pcf8574_Controls20.pinMode(P0, INPUT); // Over Temperature alert
        pcf8574_Controls20.pinMode(P1, OUTPUT); // EFUSE_EN (not going to use since it will turn off the computer)
        pcf8574_Controls20.pinMode(P2, INPUT); // OC Fault
      }
      pcf8574_Controls20.begin();

      // Set the pinModes for right expander in schematic
      pcf8574_Controls21.pinMode(P0, OUTPUT); // Enable Efuse
      pcf8574_Controls21.pinMode(P1, INPUT); // Over current fault
      pcf8574_Controls21.pinMode(P2, INPUT); // Over "Temperature" Alert 
      pcf8574_Controls21.pinMode(P6, OUTPUT); // RESET ADC (just tie high use)
      // Reset of the pins are not used
      pcf8574_Controls21.begin();

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
      ads.setConversionMode(CONTINUOUS);
      if(i == max_channels - 1){ // motherboard
        ads.readSingleEnded(3, 1); // start the conversion of 3 since it will always convert (never need to change)
      }
      // A1 feedback, A2 SPEED, A3 Current

      // resets for either arduino mega or panda (default them to high or not reset)
      pinMode(4, OUTPUT);
      pinMode(5, OUTPUT);
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);

      ///////////////
      // LOAD CELL //
      ///////////////
      if(nau.begin()){ // meed to check if it can begin otherwise it will hang the program
        nau.setLDO(NAU7802_3V0);
        nau.setGain(NAU7802_GAIN_128);
        nau.setRate(NAU7802_RATE_10SPS);
        nau.calibrate(NAU7802_CALMOD_INTERNAL);
        nau.calibrate(NAU7802_CALMOD_OFFSET);
        nau_check[i] = 1;
      }

      //////////////////
      // Thermocouple //
      //////////////////
      if(mcp.begin(0x67)){
        mcp.setADCresolution(MCP9600_ADCRESOLUTION_12);

        mcp.setThermocoupleType(MCP9600_TYPE_K);
        mcp.setFilterCoefficient(0);
        mcp_check[i] = 1;
      }

      ////////////////
      // 2. I2C IMU //
      ////////////////


      delay(100);
      if(TestArduinoScript)
        Serial.println(i);
    }
    if(TestArduinoScript)
      Serial.println("done!"); 
}

void command_finder(uint8_t index, String command_from_python){
  if(TestArduinoScript)
    Serial.println(index);
  switch (index) {
        case 0:
            startup_command(command_from_python);
            break;
        case 1:
            control_motor(command_from_python);
            break;
        case 2:
            control_actuator(command_from_python);
            break;
        case 3:
            motor_diagnostic_start(command_from_python, false); // no speed
            break;
        case 4:
            motor_diagnostic(command_from_python, false); // no speed
            break;
        case 5:
            motor_diagnostic_start(command_from_python, true); // yes speed
            break;
        case 6:
            motor_diagnostic(command_from_python, true); // yes speed
            break;
        case 7:
            actuator_diagnostic_start(command_from_python, false); // mo feedback
            break; 
        case 8:
            actuator_diagnostic(command_from_python, false); // mo feedback
            break; 
        case 9:
            actuator_diagnostic_start(command_from_python, true); // yes feedback
            break;
        case 10:
            actuator_diagnostic(command_from_python, true); // yes feedback
            break;    
        case 11:
            diagnostics_motherboard(command_from_python);
            break;
        case 12:
            load_cell_and_temp_diagnostics(command_from_python);
            break;
        case 13:
            diagnostics_IMU(command_from_python);
            break;
        // Add cases for additional words as needed
    }
}

// startup to select between arduinos
// startup LOW_HIGH
void startup_command(String command_from_python){
  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and the end

  if(number1String == "high"){
    Channel_Offset = 9;
    for(uint8_t i = 0; i < max_channels; i++){
      PWM_Channel[i] = Panda[i];
      pinMode(PWM_Channel[i], OUTPUT);
    }
  }
  else{
    Channel_Offset = 1;
    for(uint8_t i = 0; i < max_channels; i++){
      PWM_Channel[i] = Mega[i];
      pinMode(PWM_Channel[i], OUTPUT);
    }
  }

  Serial.println(Channel_Offset);
}

// control motor
// cMotor Channel# EN EN_EFUSE PWM FR BRAKE 
void control_motor(String command_from_python){
  if(TestArduinoScript)
    Serial.println("Controling the motor (change PWM and DIR signals)");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space
  uint8_t space2 = command_from_python.indexOf(' ', space1 + 1); // get it after the next space
  uint8_t space3 = command_from_python.indexOf(' ', space2 + 1); // get it after the next space
  uint8_t space4 = command_from_python.indexOf(' ', space3 + 1); // get it after the next space
  uint8_t space5 = command_from_python.indexOf(' ', space4 + 1); // get it after the next space
  uint8_t space6 = command_from_python.indexOf(' ', space5 + 1); // get it after the next space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1, space2); // between space1 + 1 and space2
  String number2String = command_from_python.substring(space2 + 1, space3); // between space2 + 1 and space3
  String number3String = command_from_python.substring(space3 + 1, space4); // between space3 + 1 and space4
  String number4String = command_from_python.substring(space4 + 1, space5); // between space4 + 1 and space5
  String number5String = command_from_python.substring(space5 + 1, space6); // between space5 + 1 and space6
  String number6String = command_from_python.substring(space6 + 1); // between space6 + 1 and the end

  uint8_t Channel = number1String.toInt();
  bool EN = number2String.toInt();
  bool EN_EFUSE = number3String.toInt();
  uint8_t PWM = number4String.toInt();
  bool FR = number5String.toInt();
  bool BREAK = number6String.toInt();


  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }
    I2CMux.closeAll();
    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }

  if(vals[Channel-Channel_Offset][0] != EN){
    if(TestArduinoScript)
      Serial.println("ENable Motor");
    pcf8574_Controls20.digitalWrite(P1, EN); // change EN
    vals[Channel-Channel_Offset][0] = EN;
  }

  if(vals[Channel-Channel_Offset][1] != EN_EFUSE){
    if(TestArduinoScript)
      Serial.println("EN_EFUSE");
    pcf8574_Controls21.digitalWrite(P0, EN_EFUSE); // Enable Efuse
    vals[Channel-Channel_Offset][1] = EN_EFUSE;
  }

  if(vals[Channel-Channel_Offset][2] != PWM){
    if(TestArduinoScript)
      Serial.println("PWM ");
    analogWrite(PWM_Channel[Channel-Channel_Offset], PWM);
    vals[Channel-Channel_Offset][2] = PWM;
  }

  if(vals[Channel-Channel_Offset][3] != FR){
    if(TestArduinoScript)
      Serial.println("FR");
    pcf8574_Controls20.digitalWrite(P0, FR);
    vals[Channel-Channel_Offset][3] = FR;
  }

  if(vals[Channel-Channel_Offset][4] != BREAK){
    if(TestArduinoScript)
      Serial.println("BREAK");
    pcf8574_Controls20.digitalWrite(P2, BREAK); // Brake
    vals[Channel-Channel_Offset][4] = BREAK;
  }


  if(TestArduinoScript){
    Serial.println(Channel);
    Serial.println(EN);
    Serial.println(EN_EFUSE);
    Serial.println(PWM);
    Serial.println(FR);
    Serial.println(BREAK);
  }

  // Serial.println("done!");
  Serial.print(Channel);
  Serial.print(" ");
  Serial.print(EN);
  Serial.print(" ");
  Serial.print(EN_EFUSE);
  Serial.print(" ");
  Serial.print(PWM);
  Serial.print(" (");
  Serial.print(PWM_Channel[Channel-Channel_Offset]);
  Serial.print(") ");
  Serial.print(FR);
  Serial.print(" ");
  Serial.println(BREAK);
}
// control actuator
// cActutor Channel# EN_EFUSE FR PWM
void control_actuator(String command_from_python){
  if(TestArduinoScript)
    Serial.println("Controling the actuator (change PWM and DIR signals)");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space
  uint8_t space2 = command_from_python.indexOf(' ', space1 + 1); // get it after the next space
  uint8_t space3 = command_from_python.indexOf(' ', space2 + 1); // get it after the next space
  uint8_t space4 = command_from_python.indexOf(' ', space3 + 1); // get it after the next space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1, space2); // between space1 + 1 and space2
  String number2String = command_from_python.substring(space2 + 1, space3); // between space2 + 1 and space3
  String number3String = command_from_python.substring(space3 + 1, space4); // between space3 + 1 and space4
  String number4String = command_from_python.substring(space4 + 1); // between space4 + 1 and the end

  uint8_t Channel = number1String.toInt();
  bool EN_EFUSE = number2String.toInt();
  bool FR = number3String.toInt();
  uint8_t PWM = number4String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }
    
    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }

  if(vals[Channel-Channel_Offset][0] != EN_EFUSE){
    if(TestArduinoScript)
      Serial.println("EN_EFUSE");
    pcf8574_Controls21.digitalWrite(P0, EN_EFUSE); // Enable Efuse
    vals[Channel-Channel_Offset][0] = EN_EFUSE;
  }

  int8_t direction = 0; // needs to be negative

  if(vals[Channel-Channel_Offset][1] != PWM || vals[Channel-Channel_Offset][2] != FR){
    if(TestArduinoScript)
      Serial.println("H-bridge majik");
    direction = 1;
    if(FR == 1){
      direction = 1;
    }
    else
      direction = -1;
    vnh.H_bridge_change(PWM_Channel[Channel-Channel_Offset], PWM, direction, stateA[Channel-Channel_Offset], stateB[Channel-Channel_Offset]);
    vals[Channel-Channel_Offset][1] = PWM;
    vals[Channel-Channel_Offset][2] = FR;
  }

  if(TestArduinoScript){
    Serial.println(Channel);
    Serial.println(EN_EFUSE);
    Serial.println(FR);
    Serial.println(PWM);
  }

  // Serial.println("done!");
  Serial.print(Channel);
  Serial.print(" ");
  Serial.print(EN_EFUSE);
  Serial.print(" ");
  Serial.print(FR);
  Serial.print(" ");
  Serial.print(PWM);
  Serial.print(" (");
  Serial.print(PWM_Channel[Channel-Channel_Offset]);
  Serial.print(" ");
  Serial.print(direction);
  Serial.println(") ");
}

// sMotorCurrent Channel# (starts the current conversion)
// sMotorSpeed Channel#  (starts the speed conversion)
void motor_diagnostic_start(String command_from_python, bool Speed_bool){
  if(TestArduinoScript)
    Serial.println("Ping the ADC Motor");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }
    I2CMux.closeAll();
    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }
  
  if(Speed_bool == false){
    // start current
    ads.readSingleEnded(2, 1);
  }
  else{
    ads.readSingleEnded(1, 1);
  }

  Serial.println("done!");

}

// get motor diagnostic data
// dMotor Channel#                      you get this: ALARM TEMP CURRENT OC_FAULT
// dMotorSpeed Channel#                 you get this: SPEED
void motor_diagnostic(String command_from_python, bool Speed_bool){
  if(TestArduinoScript)
    Serial.println("Get the motor diagnostic data (ping the ADC and the temp sensor)");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }
    I2CMux.closeAll();
    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }


  if(TestArduinoScript)
    Serial.println(Speed_bool);

  if(Speed_bool == false){
    // alarm print
    Serial.print(pcf8574_Controls20.digitalRead(P4)); // Alarm from Motor
    Serial.print(" ");

    // temp
    tmp1075.setConversionTime(TMP1075::ConversionTime27_5ms);
    Serial.print(tmp1075.getTemperatureCelsius());
    Serial.print(" ");

    // current
    Serial.print(ads.readSingleEnded(2, 0)*MAX_CURRENT/pow(2,23),5);
    Serial.print(" ");

    // OC fault
    Serial.println(pcf8574_Controls21.digitalRead(P1)); // Over current fault
  }
  else{
    // speed
    Serial.println(ads.readSingleEnded(1, 0)*MAX_SPEED/pow(2,23),5);
  }

}

// sActuatorCurrent Channel# (starts the current conversion)
// sActuatrFeeback Channel# (starts the feedback conversion)
void actuator_diagnostic_start(String  command_from_python, bool feeback_T_F){
  if(TestArduinoScript)
      Serial.println("Ping the ADC Actuator");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }
    
    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }
  
  if(feeback_T_F == false){
    // start current
    ads.readSingleEnded(2, 1);
  }
  else{
    ads.readSingleEnded(0, 1);
  }

  Serial.println("done!");
}

// get actuator diagnostic data
// dActuator Channel#                   you get this: TEMP CURRENT OC_FAULT
// dActuatrFeeback Channel# FEEBACK    you get this: FEEDBACK
void actuator_diagnostic(String command_from_python, bool feeback_T_F){
  if(TestArduinoScript)
    Serial.println("Get the actuator diagnostic data (ping the ADC and the temp sensor)");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }
    
    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }

  if(TestArduinoScript)
    Serial.println(feeback_T_F);

  if(feeback_T_F == false){
    // temp
    tmp1075.setConversionTime(TMP1075::ConversionTime27_5ms);
    Serial.print(tmp1075.getTemperatureCelsius());
    Serial.print(" ");

    // current
    Serial.print(ads.readSingleEnded(2, 0)*MAX_CURRENT/pow(2,23),5);
    Serial.print(" ");

    // OC fault
    Serial.println(pcf8574_Controls21.digitalRead(P1)); // Over current fault
  }
  else{
    // feedback
    Serial.println(ads.readSingleEnded(0, 0)*MAX_SPEED/pow(2,23),5);
  }

}

// cMotherboard Channel# _, _, ...     
void load_cell_and_temp_diagnostics(String command_from_python){
  if(TestArduinoScript)
    Serial.println("load cell and temp diagnostics");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }

    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }

  // do load cell and temp stuff...
  if(nau_check[Channel-Channel_Offset]){
    Serial.print(nau.read()); // print the actual value
  }
  else{
    Serial.print("0.0"); // print bad value
  }

  Serial.print(" ");

  if(mcp_check[Channel-Channel_Offset]){
    Serial.println(mcp.readThermocouple()); // print the actual value
  }
  else{
    Serial.println("0.0"); // print bad value
  }
}

// dMotherboard Channel#                 you get this: _, _, ...  
void diagnostics_motherboard(String command_from_python){
  if(TestArduinoScript)
    Serial.println("Motherboard diagnostics");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }

    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }

  // diagnostics for motherboard .. 
  // alarm print
  Serial.print(pcf8574_Controls20.digitalRead(P0)); // Alarm from Motor
  Serial.print(" ");

  // temp
  tmp1075.setConversionTime(TMP1075::ConversionTime27_5ms);
  Serial.print(tmp1075.getTemperatureCelsius());
  Serial.print(" ");

  // current
  Serial.print(ads.readSingleEnded(3, 0)*MAX_CURRENT/pow(2,23),5);
  Serial.print(" ");

  // OC fault
  Serial.println(pcf8574_Controls21.digitalRead(P2)); // Over current fault

}

// dIMU Channel#                 you get this: _, _, ...  
void diagnostics_IMU(String command_from_python){
  if(TestArduinoScript)
    Serial.println("IMU diagnostics");

  // get the locations of the commands
  uint8_t space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  uint8_t Channel = number1String.toInt();

  // <------------------------------------------------------------------------------------------------------------------------------------------ (channel selector code needs to be written)
  if(Channel != Channel_Selected){ // a new channel has been selected update. update the mux
    if(TestArduinoScript){
      Serial.print("Moved over to Channel ");
      Serial.println(Channel);
    }

    I2CMux.openChannel(Channel-Channel_Offset);
    // store this channel now
    Channel_Selected = Channel;
  }

  // diagnostics for IMU .. 
  ////////////////
  // 3. I2C IMU //
  ////////////////

}

void loop() {
    // Fun communication! (first test all functions at once then communicate with python)
    if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');

      // Iterate over the array of target words
      for (int i = 0; i < (sizeof(commands) / sizeof(commands[0])); i++) {
          // Check if the data contains the current target word
          if (data.indexOf(commands[i]) != -1) {
              // Call a function corresponding to the found word
              command_finder(i, data);
              break; // Exit the loop if a word is found
          }
      }
    }
}
