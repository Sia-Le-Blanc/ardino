// hardware/arduino/room_controller.ino 수정본 (실습 코드 핀 번호에 맞춤)

#include <DHT.h>
#include <Servo.h>
#include <TM1637Display.h>

// 핀 정의 (실습 코드와 동일하게)
#define DHT_PIN 2
#define DHT_TYPE DHT11
#define SERVO_PIN 8
#define RGB_R 5
#define RGB_G 6
#define RGB_B 11
#define BUZZER_PIN 3
#define TM_CLK 9
#define TM_DIO 10

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
    
    // 0-255 범위 제한
    r = constrain(r, 0, 255);
    g = constrain(g, 0, 255);
    b = constrain(b, 0, 255);
    
    setRGB(r, g, b);
  }
  else if (cmd.startsWith("SERVO=")) {
    int degree = cmd.substring(6).toInt();
    
    // 0-180 범위 제한
    degree = constrain(degree, 0, 180);
    
    lightServo.write(degree);
  }
  else if (cmd.startsWith("BUZZER=")) {
    int freq = cmd.substring(7).toInt();
    
    // 0-5000Hz 범위 제한
    if (freq > 0 && freq <= 5000) {
      tone(BUZZER_PIN, freq);
    } else {
      noTone(BUZZER_PIN);
    }
  }
  else if (cmd.startsWith("TIME=")) {
    int timeValue = cmd.substring(5).toInt();
    
    // 0-2359 범위 제한 (00:00 ~ 23:59)
    timeValue = constrain(timeValue, 0, 2359);
    
    display.showNumberDecEx(timeValue, 0b01000000, true);
  }
  else if (cmd == "TEMPERATURE=?") {
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
      Serial.print("TEMPERATURE=");
      Serial.println(temp);
    } else {
      Serial.print("TEMPERATURE=");
      Serial.println(0);
    }
  }
  else if (cmd == "HUMIDITY=?") {
    float hum = dht.readHumidity();
    if (!isnan(hum)) {
      Serial.print("HUMIDITY=");
      Serial.println(hum);
    } else {
      Serial.print("HUMIDITY=");
      Serial.println(0);
    }
  }
}

void setRGB(int r, int g, int b) {
  analogWrite(RGB_R, r);
  analogWrite(RGB_G, g);
  analogWrite(RGB_B, b);
}