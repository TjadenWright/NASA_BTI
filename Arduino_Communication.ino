const int ledPin1 = 5;  // Define a pin for the first LED
const int ledPin2 = 6;  // Define a pin for the second LED

int val1;
int val2;

void setup() {
  Serial.begin(115200);
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n'); // Read the data until a newline character is received
    sscanf(data.c_str(), "%d,%d", &val1, &val2); // Parse the integers from the received data

    // Now, you can use val1 and val2 as your two integers
    // For example, you can control two LEDs based on these values
    analogWrite(ledPin1, val1);
    analogWrite(ledPin2, val2);
  }
}

// analogWrite(ledPin, command);
