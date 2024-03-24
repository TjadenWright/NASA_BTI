#include <Arduino.h>
#include <Wire.h>
#include "PCF8574.h" // controlling the I2C gpio expander
#include <TMP1075.h> // reading I2C temeperature sensor
#include "VNH7070.h" // controlling H-Bridge
#include <ADS1219.h>
#include "TCA9548A.h"
#include <avr/wdt.h>

#define TestArduinoScript false
#define Arduino_or_latte true // true -> arduino mega / false -> latte

#define MAX_SPEED 4.96
#define MAX_CURRENT 5000*(1/22.2) // 22.2 mV/A or 0.045 A/mV 
#define MAX_FEEDBACK 4.96

String commands[] = {"startup", "cMotor", "cActuator", "sMotorCurrent", "dMotor", "sMotrSpeed", "dMotrSpeed", "sActuatorCurrent", "dActuator", "sActuatrFeeback", "dActuatrFeeback", "cMotherboard", "dMotherboard", "dIMU", "reset"}; 

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
// cMotherboard Channel# _, _, ...     
// dMotherboard Channel#                 you get this: _, _, ...
// dIMU Channel#                         you get this: _, _, ...

// check values
const int max_channels = 8; // for commands channel# doesn't count
const int max_input_outputs = 6;

// PWM channel pins
int Mega[max_channels] = {6, 13, 10, 11, 8, 9, 7, 12}; // flip 6 and 12 for the real deal
// Mega reset = 5
int Panda[max_channels] = {13, 12, 11, 10, 9, 8, 7, -1}; // (negative one is a place holder)
// Panda reset = 4

int PWM_Channel[max_channels];
int Channel_Offset = 1;   // either 1 for 1-8 or 9 for 9-16
int Channel_Selected = -1; // start with a channel we can't be in

int stateA[max_channels] = {0, 0, 0, 0, 0, 0, 0, 0};
int stateB[max_channels] = {0, 0, 0, 0, 0, 0, 0, 0};

int vals[max_channels][6];


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

    // setup vals array
    for(int i = 0; i < max_channels; i++)
      for(int j = 0; j < max_input_outputs; j++)
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
    I2CMux.closeAll();              // Set a base state which we know (also the default state on power on)

    ////////////////////
    // GPIO Expanders //
    ////////////////////
    // Set the pinModes for left expander in schematic
    pcf8574_Controls20.pinMode(P0, OUTPUT); // Forward/Reverse
    pcf8574_Controls20.pinMode(P1, OUTPUT); // Motor Enable
    pcf8574_Controls20.pinMode(P2, OUTPUT); // Brake
    // PIN3 is being used in ADC for DRDY (already setup in the function)
    pcf8574_Controls20.pinMode(P4, INPUT); // Alarm from Motor
    // PIN5-7 are already used in the VNH7070 function
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
    // A1 feedback, A2 SPEED, A3 Current

    // resets for either arduino mega or panda (default them to high or not reset)
    pinMode(4, OUTPUT);
    pinMode(5, OUTPUT);
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);

    ////////////////
    // 2. I2C IMU //
    ////////////////
}

void command_finder(int index, String command_from_python){
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
            control_motherboard(command_from_python);
            break;
        case 12:
            diagnostics_motherboard(command_from_python);
            break;
        case 13:
            diagnostics_IMU(command_from_python);
            break;
        case 14:
            // asm volatile(" jmp 0"); // reset arduino
            wdt_enable(WDTO_15MS);
            while(true);
            break;
        // Add cases for additional words as needed
    }
}

// startup to select between arduinos
// startup LOW_HIGH
void startup_command(String command_from_python){
  // Serial.println("Choose the correct channel");

  // get the locations of the commands
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and the end

  if(number1String == "high"){
    Channel_Offset = 9;
    for(int i = 0; i < max_channels; i++){
      PWM_Channel[i] = Panda[i];
      pinMode(PWM_Channel[i], OUTPUT);
    }
  }
  else{
    Channel_Offset = 1;
    for(int i = 0; i < max_channels; i++){
      PWM_Channel[i] = Mega[i];
      pinMode(PWM_Channel[i], OUTPUT);
    }
  }

  // else low keep the same
  // Serial.println(Channel_Offset);
  Serial.println("done!");
}

// control motor
// cMotor Channel# EN EN_EFUSE PWM FR BRAKE 
void control_motor(String command_from_python){
  if(TestArduinoScript)
    Serial.println("Controling the motor (change PWM and DIR signals)");

  // get the locations of the commands
  int space1 = command_from_python.indexOf(' '); // get the thing after the space
  int space2 = command_from_python.indexOf(' ', space1 + 1); // get it after the next space
  int space3 = command_from_python.indexOf(' ', space2 + 1); // get it after the next space
  int space4 = command_from_python.indexOf(' ', space3 + 1); // get it after the next space
  int space5 = command_from_python.indexOf(' ', space4 + 1); // get it after the next space
  int space6 = command_from_python.indexOf(' ', space5 + 1); // get it after the next space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1, space2); // between space1 + 1 and space2
  String number2String = command_from_python.substring(space2 + 1, space3); // between space2 + 1 and space3
  String number3String = command_from_python.substring(space3 + 1, space4); // between space3 + 1 and space4
  String number4String = command_from_python.substring(space4 + 1, space5); // between space4 + 1 and space5
  String number5String = command_from_python.substring(space5 + 1, space6); // between space5 + 1 and space6
  String number6String = command_from_python.substring(space6 + 1); // between space6 + 1 and the end

  int Channel = number1String.toInt();
  int EN = number2String.toInt();
  int EN_EFUSE = number3String.toInt();
  int PWM = number4String.toInt();
  int FR = number5String.toInt();
  int BREAK = number6String.toInt();


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
  int space1 = command_from_python.indexOf(' '); // get the thing after the space
  int space2 = command_from_python.indexOf(' ', space1 + 1); // get it after the next space
  int space3 = command_from_python.indexOf(' ', space2 + 1); // get it after the next space
  int space4 = command_from_python.indexOf(' ', space3 + 1); // get it after the next space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1, space2); // between space1 + 1 and space2
  String number2String = command_from_python.substring(space2 + 1, space3); // between space2 + 1 and space3
  String number3String = command_from_python.substring(space3 + 1, space4); // between space3 + 1 and space4
  String number4String = command_from_python.substring(space4 + 1); // between space4 + 1 and the end

  int Channel = number1String.toInt();
  int EN_EFUSE = number2String.toInt();
  int FR = number3String.toInt();
  int PWM = number4String.toInt();

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

  int direction = 0;

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
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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
void control_motherboard(String command_from_python){
  if(TestArduinoScript)
    Serial.println("Motherboard control");

  // get the locations of the commands
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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

  // do motherboard stuff...

}

// dMotherboard Channel#                 you get this: _, _, ...  
void diagnostics_motherboard(String command_from_python){
  if(TestArduinoScript)
    Serial.println("Motherboard diagnostics");

  // get the locations of the commands
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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

}

// dIMU Channel#                 you get this: _, _, ...  
void diagnostics_IMU(String command_from_python){
  if(TestArduinoScript)
    Serial.println("IMU diagnostics");

  // get the locations of the commands
  int space1 = command_from_python.indexOf(' '); // get the thing after the space

  // get the strings
  String number1String = command_from_python.substring(space1 + 1); // between space1 + 1 and space2

  int Channel = number1String.toInt();

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
