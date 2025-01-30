#include <ServoEasing.hpp>
#include <math.h>

#define DEFAULT_MICROSECONDS_FOR_0_DEGREE 500
#define DEFAULT_MICROSECONDS_FOR_180_DEGREE 2500

const int SERVO_PIN_7 = 7;
const int SERVO_PIN_8 = 6;
const int SERVO_PIN_9 = 5;

const int SERVO_ANGLE_0 = 50;
const int SERVO_ANGLE_1 = 90;
const int SERVO_ANGLE_2 = 180;

ServoEasing servo0, servo1, servo2;

const int TO_END_RIGHT = 5;
const int TO_END_LEFT = 175;

const int SERVO_SPEED = 25;

bool movingRight = true;
bool changeRotation = false;

void initializeServos() {
  servo0.attach(SERVO_PIN_7, DEFAULT_MICROSECONDS_FOR_0_DEGREE, DEFAULT_MICROSECONDS_FOR_180_DEGREE, 0, 180);
  servo1.attach(SERVO_PIN_8, DEFAULT_MICROSECONDS_FOR_0_DEGREE, DEFAULT_MICROSECONDS_FOR_180_DEGREE, 0, 180);
  servo2.attach(SERVO_PIN_9, DEFAULT_MICROSECONDS_FOR_0_DEGREE, DEFAULT_MICROSECONDS_FOR_180_DEGREE, 0, 180);

  servo0.setEasingType(EASE_LINEAR);
  servo2.setEasingType(EASE_LINEAR);
  servo1.setEasingType(EASE_LINEAR);

  servo0.write(SERVO_ANGLE_0);
  servo1.write(SERVO_ANGLE_1);
  servo2.write(SERVO_ANGLE_2);

}

void checkSerialCommand() {
  if(Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "C"){
      changeRotation = true;
    }
  }
}

void moveServo(int targetAngle) {
  int currentAngle = servo1.getCurrentAngle();

  if(targetAngle > currentAngle) {
    for (int angle = currentAngle; angle <= targetAngle; angle++){
      checkSerialCommand();
      if(changeRotation) {
        movingRight = !movingRight;
        changeRotation = false;
        delay(500);
        Serial.println("OK");
        break;
      }
      servo1.write(angle);
      delay(SERVO_SPEED);
    }
  }else {
    for (int angle = currentAngle; angle>= targetAngle; angle--) {
      checkSerialCommand();
      if(changeRotation) {
        movingRight = !movingRight;
        changeRotation = false;
        delay(500);
        Serial.println("OK");
        break;
      }
      servo1.write(angle);
      delay(SERVO_SPEED);
    }
  }
}

void setup() {
  

  Serial.begin(9600);
  initializeServos();
  setSpeedForAllServos(SERVO_SPEED);
  Serial.println("System is ready to go");
}

void loop() {
  checkSerialCommand();
  
  //if(changeRotation) {
    //movingRight = !movingRight;
    //changeRotation = false;
  //}

  if(movingRight) {
      moveServo(TO_END_RIGHT);
      movingRight = false;
    } else {
      moveServo(TO_END_LEFT);
      movingRight = true;
    }
  

}
