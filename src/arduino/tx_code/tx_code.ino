#define SOFT_SPI_MISO_PIN 6
#define SOFT_SPI_MOSI_PIN 5
#define SOFT_SPI_SCK_PIN  4

#include <SPI.h>
#include <DigitalIO.h> 
#include <RF24.h>

#define CE_PIN   9
#define CSN_PIN  10

RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001"; 

char inputBuffer[64];
int bufferIdx = 0;

void setup() {
  Serial.begin(9600); 
  
  if (!radio.begin()) {
    // If it gets stuck here, the Arduino cannot talk to the nRF24 chip!
    while (1) {
      Serial.println("RF24 Hardware Error!");
      delay(1000);
    }
  }
  
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW); 
  radio.stopListening();
  
  Serial.println("ready"); 
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    if (c == '\n') {
      inputBuffer[bufferIdx] = '\0'; // Null-terminate string
      
      // Broadcast it over the air instantly
      radio.write(&inputBuffer, sizeof(inputBuffer));
      
      bufferIdx = 0; // Reset buffer
    } else if (bufferIdx < 63) {
      inputBuffer[bufferIdx++] = c;
    }
  }
}