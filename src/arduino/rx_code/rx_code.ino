#define SOFT_SPI_MISO_PIN 6
#define SOFT_SPI_MOSI_PIN 5
#define SOFT_SPI_SCK_PIN  4

#include <SPI.h>
#include <DigitalIO.h> 
#include <RF24.h>
#include <Servo.h>

#define CE_PIN   9
#define CSN_PIN  10

// Safe servo pin assignments avoiding SPI pins 4, 5, 6, 9, 10
#define THROTTLE_PIN 2
#define PITCH_PIN    3
#define ROLL_PIN     7
#define YAW_PIN      8

RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001"; 

Servo throttleServo, pitchServo, rollServo, yawServo;

// Base values matching python map bounds
uint8_t throttle_value = 0;
uint8_t pitch_value = 127;
uint8_t roll_value = 127;
uint8_t yaw_value = 127;

unsigned long lastReceiveTime = 0;
const unsigned long FAILSAFE_TIMEOUT = 2000; // Failsafe triggers after 2 seconds

void setup() {
  Serial.begin(9600);
  
  if (!radio.begin()) {
    while (1); 
  }
  
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening(); 

  // Initialize servos
  throttleServo.attach(THROTTLE_PIN);
  pitchServo.attach(PITCH_PIN);
  rollServo.attach(ROLL_PIN);
  yawServo.attach(YAW_PIN);
  
  // Set neutral safe positions
  throttleServo.write(0);
  pitchServo.write(90);
  rollServo.write(90);
  yawServo.write(90);
  
  lastReceiveTime = millis();
}

void loop() {
  if (radio.available()) {
    char receivedMessage[64] = {0};
    radio.read(&receivedMessage, sizeof(receivedMessage));
    
    // Extract and parse channel strings
    parseMessage(receivedMessage);
    lastReceiveTime = millis(); 
  }
  
  // Failsafe condition: If data stream stops, cut throttle
  if (millis() - lastReceiveTime > FAILSAFE_TIMEOUT) {
    throttle_value = 0; 
  }
  
  applyControls();
}

void parseMessage(char* message) {
  // Named format handler: "P:throttle:128,pitch:200..."
  if (strstr(message, "P:") != NULL) {
    char* token = strtok(message + 2, ","); // Skip "P:" prefix
    while (token != NULL) {
      char* colon = strchr(token, ':');
      if (colon != NULL) {
        *colon = '\0';
        char* channel = token;
        uint8_t value = (uint8_t)atoi(colon + 1);
        
        if (strcmp(channel, "throttle") == 0) throttle_value = value;
        else if (strcmp(channel, "pitch") == 0) pitch_value = value;
        else if (strcmp(channel, "roll") == 0)  roll_value = value;
        else if (strcmp(channel, "yaw") == 0)   yaw_value = value;
      }
      token = strtok(NULL, ",");
    }
  } 
  // Simple format handler: "128,200,120,150"
  else {
    uint8_t values[4] = {0, 127, 127, 127};
    int count = 0;
    char* token = strtok(message, ",");
    while (token != NULL && count < 4) {
      values[count++] = (uint8_t)constrain(atoi(token), 0, 255);
      token = strtok(NULL, ",");
    }
    throttle_value = values[0];
    pitch_value    = values[1];
    roll_value     = values[2];
    yaw_value      = values[3];
  }
}

void applyControls() {
  throttleServo.write(map(throttle_value, 0, 255, 0, 180));
  pitchServo.write(map(pitch_value, 0, 255, 0, 180));
  rollServo.write(map(roll_value, 0, 255, 0, 180));
  yawServo.write(map(yaw_value, 0, 255, 0, 180));
}