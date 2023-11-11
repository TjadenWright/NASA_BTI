// prototype
#include <Servo.h>
Servo Servo1;

int servoPin = 5;

// front
const int front_PWM1 = 11;
const int front_PWM2 = 10;
const int front_DIR1 = 13;
const int front_DIR2 = 12;

// backc:\Users\tj10c\Downloads\esphome-basen-bms-main\esphome-basen-bms-main\esp32-ble-example.yaml
const int back_PWM1 = 9;
const int back_PWM2 = 6;
const int back_DIR1 = 8;
const int back_DIR2 = 7;

int val1 = 0; // Default PWM value for motor 1
int val2 = 0; // Default PWM value for motor 2
int dir1 = 1;
int dir2 = 1;

void setup() {
  Serial.begin(9600);
  pinMode(front_PWM1, OUTPUT);
  pinMode(front_PWM2, OUTPUT);
  pinMode(front_DIR1, OUTPUT);
  pinMode(front_DIR2, OUTPUT);
  pinMode(back_PWM1, OUTPUT);
  pinMode(back_PWM2, OUTPUT);
  pinMode(back_DIR1, OUTPUT);
  pinMode(back_DIR2, OUTPUT);

  // prototye
  Servo1.attach(servoPin);

  // pinMode(front_PWM1_test, OUTPUT);
  // pinMode(front_PWM2_test, OUTPUT);
  // pinMode(front_DIR1_test, OUTPUT);
  // pinMode(front_DIR2_test, OUTPUT);
  // pinMode(back_PWM1_test, OUTPUT);
  // pinMode(back_PWM2_test, OUTPUT);
  // pinMode(back_DIR1_test, OUTPUT);
  // pinMode(back_DIR2_test, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int parsedCount = sscanf(data.c_str(), "%d,%d,%d,%d", &val1, &val2, &dir1, &dir2);

    if (parsedCount == 3) {
      // Only 3 integers were received, set dir2 equal to dir1
      dir2 = dir1;
    }
  }

  analogWrite(front_PWM1, val2);
  analogWrite(back_PWM1, val2);
  analogWrite(front_PWM2, val1);
  analogWrite(back_PWM2, val1);

  digitalWrite(front_DIR1, dir2);
  digitalWrite(front_DIR2, dir2);
  digitalWrite(back_DIR1, dir1);
  digitalWrite(back_DIR2, dir1);

  // for(int i =0; i < 255; i++){
  //   analogWrite(front_PWM1, i);
  //   analogWrite(back_PWM1, i);
  //   analogWrite(front_PWM2, i);
  //   analogWrite(back_PWM2, i);

  //   digitalWrite(front_DIR1, HIGH);
  //   digitalWrite(front_DIR2, HIGH);
  //   digitalWrite(back_DIR1, HIGH);
  //   digitalWrite(back_DIR2, HIGH);

  //   Serial.println(i);
  //   delay(100);

  //   String data = Serial.readStringUntil('\n');
  //   sscanf(data.c_str(), "%d,%d", &val1, &val2);
  // }

  // prototype
  Servo1.write(90); // 90 degrees

}