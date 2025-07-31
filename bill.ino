#include <SoftwareSerial.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pin setup
#define TEMP_SENSOR_PIN 8
#define GAS_SENSOR_PIN A1
#define RED_LED 10
#define BLUE_LED 11

// SIM800L - Changed to pins 5 and 6
#define SIM800_TX 5  // Changed from 2
#define SIM800_RX 6  // Changed from 3
SoftwareSerial sim800(SIM800_RX, SIM800_TX);

// Temperature sensor
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature sensors(&oneWire);

// Thresholds
const float TEMP_LIMIT = 28.0;
const int GAS_LIMIT = 140;

// SMS control
unsigned long lastSMSTime = 0;
const unsigned long smsCooldown = 300000; // 5 min
String lastAlert = "";

void setup() {
  Serial.begin(9600);
  sim800.begin(9600);
  sensors.begin();
  pinMode(RED_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);

  delay(3000);  // Longer startup delay
  
  // Initialize SIM800L
  Serial.println("Initializing SIM800L...");
  sim800.println("AT");
  delay(1000);
  readSIM800Response("AT");
  
  sim800.println("AT+CMGF=1");  // SMS text mode
  delay(1000);
  readSIM800Response("CMGF");
  
  Serial.println("Setup complete");
}

void loop() {
  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);
  int gas = analogRead(GAS_SENSOR_PIN);

  Serial.print("Temp: "); Serial.println(temp);
  Serial.print("Gas: "); Serial.println(gas);

  bool tempHigh = temp > TEMP_LIMIT;
  bool gasHigh = gas > GAS_LIMIT;
  String alertType;

  if (tempHigh && gasHigh) {
    alertType = "CRITICAL";
    blinkLED(RED_LED, 5, 100);
  } else if (tempHigh) {
    alertType = "TEMP";
    blinkLED(RED_LED, 5, 100);
  } else if (gasHigh) {
    alertType = "GAS";
    blinkLED(RED_LED, 5, 100);
  } else {
    alertType = "NORMAL";
    blinkLED(BLUE_LED, 5, 100);
  }

  if (alertType != "NORMAL" && (alertType != lastAlert || millis() - lastSMSTime > smsCooldown)) {
    String message = "";
    if (alertType == "TEMP") {
      message = "High Temperature Alert!\nYour fish pond temperature is too high.\nAction: Add shade, increase flow, or add cooler water.\n– AQUA HACK | Call: 0785138874";
    } else if (alertType == "GAS") {
      message = "High Ammonia Alert\nHarmful gas detected! Change 30–50% water, stop feeding, and add aeration.\n– AQUA HACK | Call: 0785138874";
    } else if (alertType == "CRITICAL") {
      message = "Critical Pond Alert\nBoth temperature and ammonia levels are dangerously high!\nAdd shade, change water, improve aeration.\n– AQUA HACK | Call: 0785138874";
    }

    sendSMS("0770701419", message);
    lastSMSTime = millis();
    lastAlert = alertType;
  }

  delay(1000);
}

void blinkLED(int pin, int times, int delayTime) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(delayTime);
    digitalWrite(pin, LOW);
    delay(delayTime);
  }
}

void sendSMS(String number, String msg) {
  Serial.println("=== Starting SMS Send ===");
  
  // Clear any pending data
  while(sim800.available()) sim800.read();
  
  // Set SMS text mode
  sim800.println("AT+CMGF=1");
  delay(1000);
  readSIM800Response("CMGF");
  
  // Send number
  sim800.print("AT+CMGS=\"");
  sim800.print(number);
  sim800.println("\"");
  delay(1000);
  readSIM800Response("CMGS");
  
  // Send message
  sim800.print(msg);
  sim800.write(26); // Ctrl+Z
  delay(15000);  // Wait for network transmission
  readSIM800Response("Final");
  
  Serial.println("=== SMS Send Complete ===");
}

void readSIM800Response(String command) {
  Serial.print("Response to ");
  Serial.print(command);
  Serial.print(": ");
  
  unsigned long timeout = millis() + 5000;
  while(millis() < timeout) {
    if(sim800.available()) {
      String response = sim800.readString();
      Serial.println(response);
      break;
    }
  }
}