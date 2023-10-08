// front
const int front_PWM1 = 11;
const int front_PWM2 = 10;
const int front_DIR1 = 13;
const int front_DIR2 = 12;

// back
const int back_PWM1 = 9;
const int back_PWM2 = 6;
const int back_DIR1 = 8;
const int back_DIR2 = 7;

int val1 = 0; // Default PWM value for motor 1
int val2 = 0; // Default PWM value for motor 2
int dir = 1;

void setup() {
  Serial.begin(115200);
  pinMode(front_PWM1, OUTPUT);
  pinMode(front_PWM2, OUTPUT);
  pinMode(front_DIR1, OUTPUT);
  pinMode(front_DIR2, OUTPUT);
  pinMode(back_PWM1, OUTPUT);
  pinMode(back_PWM2, OUTPUT);
  pinMode(back_DIR1, OUTPUT);
  pinMode(back_DIR2, OUTPUT);

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
    sscanf(data.c_str(), "%d,%d,%d", &val1, &val2, &dir);
  }

  analogWrite(front_PWM1, val2);
  analogWrite(back_PWM1, val2);
  analogWrite(front_PWM2, val1);
  analogWrite(back_PWM2, val1);

  digitalWrite(front_DIR1, dir);
  digitalWrite(front_DIR2, dir);
  digitalWrite(back_DIR1, dir);
  digitalWrite(back_DIR2, dir);

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

}

