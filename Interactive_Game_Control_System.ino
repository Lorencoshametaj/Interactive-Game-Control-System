// Joystick Pins
const int VRxPin = A0;
const int VRyPin = A1;
const int SWPin = 2; // Optional, for the button

// Ultrasonic Sensor Pins
const int trigPin = 9;
const int echoPin = 10;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set the pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  // If you're using the joystick button
  pinMode(SWPin, INPUT_PULLUP);
}

long lastValidDistance = 100; // Initial value

// Joystick reading
int readJoystickX() {
  return analogRead(VRxPin);
}

int readJoystickY() {
  return analogRead(VRyPin);
}

// Ultrasonic reading
long readUltrasonicDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  
  long distance = duration * 0.034 / 2; // Convert to centimeters

  if (distance == 0 || distance > 100) {
    // Do not send the distance; use the last valid distance or set a flag
    distance = lastValidDistance;
  } else {
    lastValidDistance = distance; // Update the last valid distance
  }

  return distance;
}

void loop() {
  int xValue = readJoystickX();
  int yValue = readJoystickY();
  long distance = readUltrasonicDistance();
  int buttonState = digitalRead(SWPin); // Read the button state

  // Optional: Read the button state
  // int buttonState = digitalRead(SWPin);
  
  // Create a string with data separated by commas
  String dataString = String(xValue) + ", " + String(yValue) + ", " + String(distance) + ", " + String(buttonState);
  
  // Send data via serial
  Serial.println(dataString);
  
  delay(50); // Wait 50ms before the next reading
}
