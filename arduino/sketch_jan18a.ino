// Pin definitions
int buttonPin = A0;
int lightSensorPin = A2;

const int trigPin = 11;  // TRIG pin connected to D11
const int echoPin = 13;  // ECHO pin connected to D13

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Set button pin mode with pull-up resistor
  pinMode(buttonPin, INPUT_PULLUP);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Light sensor does not need pinMode setup since it will be read using analogRead
}

void loop() {
  // // Read the button state (digital)
  // int buttonState = digitalRead(buttonPin);

  // // Read the light sensor value (analog)
  // int lightSensorValue = analogRead(lightSensorPin);

  // // Print the button state and light sensor value
  // Serial.print("Button State: ");
  // Serial.print(buttonState);  // Prints 0 (pressed) or 1 (not pressed)
  // Serial.print(" | Light Sensor Value: ");
  // Serial.println(lightSensorValue);  // Prints analog value (0-1023)

  // // Small delay for readability
  // delay(100);

  // Send a 10-microsecond pulse to TRIG
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Measure the duration of the ECHO pulse
  long duration = pulseIn(echoPin, HIGH);

  // Calculate the distance in centimeters
  float distance = duration * 0.034 / 2;

  // Print the distance
  // Serial.print("Distance: ");
  Serial.println(distance);
  // Serial.println(" cm");

  // Delay before the next reading
  delay(100); 
}