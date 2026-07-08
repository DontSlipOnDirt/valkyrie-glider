#include <SPI.h>
#include <RF24.h>

#define CE_PIN   9
#define CSN_PIN  10

RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";

char inputBuffer[96];
int bufferIdx = 0;

void setup() {
  Serial.begin(9600);

  if (!radio.begin()) {
    while (1) {
      Serial.println("RF24 Hardware Error!");
      delay(1000);
    }
  }

  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.setChannel(76);
  radio.setDataRate(RF24_1MBPS);
  radio.enableDynamicPayloads();
  radio.stopListening();

  Serial.println("ready");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      inputBuffer[bufferIdx] = '\0';
      radio.write(inputBuffer, bufferIdx + 1); // send only what's used
      bufferIdx = 0;
    } else if (bufferIdx < 95) {
      inputBuffer[bufferIdx++] = c;
    }
  }
}