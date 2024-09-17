#include <Servo.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int r1 = 4;
const int g1 = 28;
const int r2 = 5;
const int g2 = 29;
const int r3 = 6;
const int g3 = 30;
const int r4 = 7;
const int g4 = 31;

const int IR1 = 22;
const int IR2 = 23;

const int P1 = 24;
const int P2 = 25;
const int P3 = 26;
const int P4 = 27;

Servo servo_E;
Servo servo_S;
int servo_E_position = 0;
int servo_S_position = 0;
int original_E_position = 0;
int original_S_position = 0;

unsigned long ir1HighTime = 0;
unsigned long ir2HighTime = 0;
bool ir1WasLow = false;
bool ir2WasLow = false;

int spot1State = 1;
int spot2State = 1;
int spot3State = 1;
int spot4State = 1;

int P1State = 0;
int P2State = 0;
int P3State = 0;
int P4State = 0;

void setup() {
  Serial.begin(115200);  

  pinMode(r1, OUTPUT);
  pinMode(g1, OUTPUT);
  pinMode(r2, OUTPUT);
  pinMode(g2, OUTPUT);
  pinMode(r3, OUTPUT);
  pinMode(g3, OUTPUT);
  pinMode(r4, OUTPUT);
  pinMode(g4, OUTPUT);
  pinMode(IR1, INPUT);
  pinMode(IR2, INPUT);
  pinMode(P1, INPUT);
  pinMode(P2, INPUT);
  pinMode(P3, INPUT);
  pinMode(P4, INPUT);

  servo_E.attach(2);
  servo_S.attach(3);

  lcd.init();
  lcd.backlight();
}

void loop() {

 if (digitalRead(P1) == HIGH && spot1State == 1) {
  P1State = 1;
}
else {
  P1State = 0;
}

if (digitalRead(P2) == HIGH && spot2State == 1) {
  P2State = 1;
}
else {
  P2State = 0;
}

if (digitalRead(P3) == HIGH && spot3State == 1) {
  P3State = 1;
}
else {
  P3State = 0;
}

if (digitalRead(P4) == HIGH && spot4State == 1) {
  P4State = 1;
}
else {
  P4State = 0;
}

  int ir1State = debounceRead(IR1);
  int ir2State = debounceRead(IR2);

  updateLED(1, digitalRead(P1));
  updateLED(2, digitalRead(P2));
  updateLED(3, digitalRead(P3));
  updateLED(4, digitalRead(P4));

  int totalHighStates = P1State + P2State + P3State + P4State;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Spot Free: ");
  lcd.print(totalHighStates);

  handleServoMovement(ir1State, ir1WasLow, ir1HighTime, servo_E, servo_E_position, original_E_position);
  handleServoMovement(ir2State, ir2WasLow, ir2HighTime, servo_S, servo_S_position, original_S_position);

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    handleSerialInput(input);
  }
  delay(100);
}

int debounceRead(int pin) {
  int state1 = digitalRead(pin);
  delay(50);  // Debounce delay
  int state2 = digitalRead(pin);
  return (state1 == state2) ? state1 : -1;
}

void handleServoMovement(int irState, bool &irWasLow, unsigned long &irHighTime, Servo &servo, int &servoPosition, int originalPosition) {
  if (irState == LOW && !irWasLow) {
    irWasLow = true;
    servoPosition = 70;
    moveServo(servo, servoPosition);
  } else if (irState == HIGH && irWasLow) {
    irWasLow = false;
    irHighTime = millis();
  }

  if (irState == HIGH && millis() - irHighTime >= 3000) {
    moveServo(servo, originalPosition);
  }
}

void moveServo(Servo &servo, int targetPosition) {
  int currentPosition = servo.read();
  int step = (currentPosition < targetPosition) ? 1 : -1;

  for (int pos = currentPosition; pos != targetPosition; pos += step) {
    servo.write(pos);
    delay(5);  
  }
}

void updateLED(int spot, int sensorState) {
  int redPin, greenPin;

  switch (spot) {
    case 1:
      redPin = r1;
      greenPin = g1;
      break;
    case 2:
      redPin = r2;
      greenPin = g2;
      break;
    case 3:
      redPin = r3;
      greenPin = g3;
      break;
    case 4:
      redPin = r4;
      greenPin = g4;
      break;
    default:
      return; 
  }

  if (sensorState == LOW) { 
    updateSpotState(spot, 3);  
    analogWrite(redPin, 255);  
    digitalWrite(greenPin, LOW);
    sendStatusUpdate(); 
 
    if ((spot == 1 && spot1State == 2) ||
        (spot == 2 && spot2State == 2) ||
        (spot == 3 && spot3State == 2) ||
        (spot == 4 && spot4State == 2)) {
      analogWrite(redPin, 10); 
      digitalWrite(greenPin, HIGH);  
    } 
    else  {
      updateSpotState(spot, 1); 
      analogWrite(redPin, 0); 
      digitalWrite(greenPin, HIGH);
      sendStatusUpdate();
    }
  }
}

void handleSerialInput(String input) {
  if (input.startsWith("reserve:")) {
    int spot = input.substring(8).toInt();
    updateSpotState(spot, 2); 
    int spot = input.substring(5).toInt();
    updateSpotState(spot, 1);  
  }
}

void updateSpotState(int spot, int state) {
  switch (spot) {
    case 1:
      spot1State = state;
      break;
    case 2:
      spot2State = state;
      break;
    case 3:
      spot3State = state;
      break;
    case 4:
      spot4State = state;
      break;
    default:
      Serial.println("Invalid spot number");
      return;  // Invalid spot
  }
}

void sendStatusUpdate() {
  bool shouldSend = false;

  if (spot1State == 3 || spot1State == 1 || spot1State == 2) {
    Serial.print("spot1:");
    Serial.print(spot1State);
     Serial.print(",");
    shouldSend = true;
  }
  if (spot2State == 3 || spot2State == 1 || spot2State == 2) {
    Serial.print("spot2:");
    Serial.print(spot2State);
     Serial.print(",");
    shouldSend = true;
  }
  if (spot3State == 3 || spot3State == 1 || spot3State == 2) {
    Serial.print("spot3:");
    Serial.print(spot3State);
     Serial.print(",");
    shouldSend = true;
  }
  if (spot4State == 3 || spot4State == 1 || spot4State == 2) {
    Serial.print("spot4:");
    Serial.print(spot4State);
    shouldSend = true;
  }

  if (shouldSend) {
    Serial.println();
  }
}