// room_controller.ino

#include <DHT.h>
#include <Servo.h>
#include <TM1637Display.h>

// 핀 정의
#define DHT_PIN 2
#define DHT_TYPE DHT11
#define SERVO_PIN 9
#define RGB_R 8
#define RGB_G 7
#define RGB_B 13
#define BUZZER_PIN 6
#define TM_CLK 4
#define TM_DIO 5

// 객체 초기화
DHT dht(DHT_PIN, DHT_TYPE);
Servo lightServo;
TM1637Display display(TM_CLK, TM_DIO);

void setup() {
  Serial.begin(9600);
  dht.begin();
  lightServo.attach(SERVO_PIN);
  display.setBrightness(0x0f);
  
  pinMode(RGB_R, OUTPUT);
  pinMode(RGB_G, OUTPUT);
  pinMode(RGB_B, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  setRGB(0, 0, 0);
  noTone(BUZZER_PIN);
  
  Serial.println("Arduino Ready");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    executeCommand(command);
  }
  
  delay(50);
}

void executeCommand(String cmd) {
  if (cmd.startsWith("RGB=")) {
    int r, g, b;
    sscanf(cmd.c_str(), "RGB=%d,%d,%d", &r, &g, &b);
    setRGB(r, g, b);
  }
  else if (cmd.startsWith("SERVO=")) {
    int degree = cmd.substring(6).toInt();
    lightServo.write(degree);
  }
  else if (cmd.startsWith("BUZZER=")) {
    int freq = cmd.substring(7).toInt();
    if (freq > 0) {
      tone(BUZZER_PIN, freq);
    } else {
      noTone(BUZZER_PIN);
    }
  }
  else if (cmd.startsWith("TIME=")) {
    // Python에서 "TIME=1430" 형식으로 전송 (14:30)
    int timeValue = cmd.substring(5).toInt();
    display.showNumberDecEx(timeValue, 0b01000000, true);
  }
  else if (cmd == "TEMPERATURE=?") {
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
      Serial.print("TEMPERATURE=");
      Serial.println(temp);
    }
  }
  else if (cmd == "HUMIDITY=?") {
    float hum = dht.readHumidity();
    if (!isnan(hum)) {
      Serial.print("HUMIDITY=");
      Serial.println(hum);
    }
  }
}

void setRGB(int r, int g, int b) {
  analogWrite(RGB_R, r);
  analogWrite(RGB_G, g);
  analogWrite(RGB_B, b);
}