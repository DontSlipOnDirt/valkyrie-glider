#include <SPI.h>
#include <RF24.h>
#include <Servo.h>

#define CE_PIN   9
#define CSN_PIN  10

#define THROTTLE_PIN 2   // ESC — not connected yet, harmless for now
#define PITCH_PIN    3
#define ROLL_PIN     7

RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";

Servo throttleServo, pitchServo, rollServo;

uint8_t throttle_value = 0;
uint8_t pitch_value = 127;
uint8_t roll_value = 127;

unsigned long lastReceiveTime = 0;
const unsigned long FAILSAFE_TIMEOUT = 2000;

void setup() {
  Serial.begin(9600);

  if (!radio.begin()) {
    while (1) {
      Serial.println("Nano2: RF24 hardware not detected!");
      delay(1000);
    }
  }
  Serial.println("Nano2: radio.begin() OK");

  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW);
  radio.setChannel(76);
  radio.setDataRate(RF24_1MBPS);
  radio.enableDynamicPayloads();
  radio.startListening();

  throttleServo.attach(THROTTLE_PIN);
  pitchServo.attach(PITCH_PIN);
  rollServo.attach(ROLL_PIN);

  throttleServo.write(0);   // safe idle for ESC once connected
  pitchServo.write(90);
  rollServo.write(90);

  lastReceiveTime = millis();
}

void loop() {
  if (radio.available()) {
    char receivedMessage[32] = {0};
    uint8_t len = radio.getDynamicPayloadSize();
    radio.read(&receivedMessage, len);
    //Serial.print("Nano2 received: ");
    Serial.print("Nano2 received (len=");
    Serial.print(len);
    Serial.print("): ");
    Serial.println(receivedMessage);
    //Serial.println(receivedMessage);
    parseMessage(receivedMessage);
    lastReceiveTime = millis();
  }

  if (millis() - lastReceiveTime > FAILSAFE_TIMEOUT) {
    throttle_value = 0;
  }

  applyControls();
}

void parseMessage(char* message) {
  if (strstr(message, "P:") != NULL) {
    char* token = strtok(message + 2, ",");
    while (token != NULL) {
      char* colon = strchr(token, ':');
      if (colon != NULL) {
        *colon = '\0';
        char* channel = token;
        uint8_t value = (uint8_t)atoi(colon + 1);

        if (strcmp(channel, "throttle") == 0) throttle_value = value;
        else if (strcmp(channel, "pitch") == 0) pitch_value = value;
        else if (strcmp(channel, "roll") == 0)  roll_value = value;
      }
      token = strtok(NULL, ",");
    }
  } else {
    uint8_t values[3] = {0, 127, 127};
    int count = 0;
    char* token = strtok(message, ",");
    while (token != NULL && count < 3) {
      values[count++] = (uint8_t)constrain(atoi(token), 0, 255);
      token = strtok(NULL, ",");
    }
    throttle_value = values[0];
    pitch_value    = values[1];
    roll_value     = values[2];
  }
}

void applyControls() {
  // Re-center pitch/roll from 0–255 (mid ~127) to roughly -128..+128
  int y = (int)pitch_value - 127;  // forward/back stick
  int x = (int)roll_value  - 127;  // left/right stick

  int mix1 = constrain(y + x, -128, 128);  // Servo on PITCH_PIN (3)
  int mix2 = constrain(y - x, -128, 128);  // Servo on ROLL_PIN (7)

  pitchServo.write(map(mix1, -128, 128, 60, 120)); // adjust 60/120 to your linkage throw
  rollServo.write(map(mix2, -128, 128, 60, 120));

  throttleServo.write(map(throttle_value, 0, 255, 0, 180));
}