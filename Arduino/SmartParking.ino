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

void setup() {
  Serial.begin(9600);

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
  int P1State = digitalRead(P1);
  int P2State = digitalRead(P2);
  int P3State = digitalRead(P3);
  int P4State = digitalRead(P4);

  int ir1State = digitalRead(IR1);
  int ir2State = digitalRead(IR2);

  checkPark(P1State, g1, r1);
  checkPark(P2State, g2, r2);
  checkPark(P3State, g3, r3);
  checkPark(P4State, g4, r4);

  int totalHighStates = P1State + P2State + P3State + P4State;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Spot Free: ");
  lcd.print(totalHighStates);

  // Handle servos based on IR sensors
  if (ir1State == LOW) {
    ir1WasLow = true;
    servo_E_position = 70;
    moveServo(servo_E, servo_E_position);
  } else if (ir1State == HIGH && ir1WasLow) {
    ir1WasLow = false;
    ir1HighTime = millis();
  }

  if (ir2State == LOW) {
    ir2WasLow = true;
    servo_S_position = 70;
    moveServo(servo_S, servo_S_position);
  } else if (ir2State == HIGH && ir2WasLow) {
    ir2WasLow = false;
    ir2HighTime = millis();
  }

  if (millis() - ir1HighTime >= 3000 && ir1State == HIGH) {
    moveServo(servo_E, original_E_position);
  }

  if (millis() - ir2HighTime >= 3000 && ir2State == HIGH) {  
    moveServo(servo_S, original_S_position);
  }

  // Check for serial input
  if (Serial.available()) {
    String input = Serial.readString();
    Serial.println("Received input: " + input);  // Debugging line to confirm input reception
    handleSerialInput(input);
  }

  delay(100);
}

void moveServo(Servo servo, int targetPosition) {
  int currentPosition = servo.read();

  if (currentPosition < targetPosition) {
    for (int pos = currentPosition; pos <= targetPosition; pos++) {
      servo.write(pos);
      delay(10);
    }
  } else if (currentPosition > targetPosition) {
    for (int pos = currentPosition; pos >= targetPosition; pos--) {
      servo.write(pos);
      delay(10);
    }
  }
}

void checkPark(int p, int g, int r) {
  if (p == LOW) {
    digitalWrite(r, HIGH);
    digitalWrite(g, LOW);
  } else {
    digitalWrite(g, HIGH);
    digitalWrite(r, LOW);
  }
}

void handleSerialInput(String input) {
  if (input.startsWith("reserve:")) {
    int spot = input.substring(8).toInt();
    if (spot == 1) {
      analogWrite(r1, 10);
      digitalWrite(g1, HIGH);

    } else if (spot == 2) {
      analogWrite(r2, 10);
      digitalWrite(g2, HIGH);

    } else if (spot == 3) {
      analogWrite(r3, 10);
      digitalWrite(g3, HIGH);

    } else if (spot == 4) {
      analogWrite(r4, 10);
      digitalWrite(g4, HIGH);
    }
  }
}
