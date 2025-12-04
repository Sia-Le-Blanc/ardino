// hardware/arduino/room_controller.ino (실습 코드 기반)

#include <Servo.h>
#include <TM1637Display.h>

// 핀 정의
#define DHT_PIN 2
#define SERVO_PIN 8
#define RGB_R 5
#define RGB_G 6
#define RGB_B 11
#define BUZZER_PIN 3
#define TM_CLK 9
#define TM_DIO 10

// 객체 초기화
Servo lightServo;
TM1637Display display(TM_CLK, TM_DIO);

// DHT11 변수
float temperature = 0.0;
float humidity = 0.0;

void setup() {
  Serial.begin(9600);
  lightServo.attach(SERVO_PIN);
  display.setBrightness(0x0f);
  
  pinMode(DHT_PIN, INPUT);
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
    r = constrain(r, 0, 255);
    g = constrain(g, 0, 255);
    b = constrain(b, 0, 255);
    setRGB(r, g, b);
  }
  else if (cmd.startsWith("SERVO=")) {
    int degree = cmd.substring(6).toInt();
    degree = constrain(degree, 0, 180);
    lightServo.write(degree);
  }
  else if (cmd.startsWith("BUZZER=")) {
    int freq = cmd.substring(7).toInt();
    if (freq > 0 && freq <= 5000) {
      tone(BUZZER_PIN, freq);
    } else {
      noTone(BUZZER_PIN);
    }
  }
  else if (cmd.startsWith("TIME=")) {
    int timeValue = cmd.substring(5).toInt();
    timeValue = constrain(timeValue, 0, 2359);
    display.showNumberDecEx(timeValue, 0b01000000, true);
  }
  else if (cmd == "TEMPERATURE=?") {
    readDHT11();
    Serial.print("TEMPERATURE=");
    Serial.println(temperature);
  }
  else if (cmd == "HUMIDITY=?") {
    readDHT11();
    Serial.print("HUMIDITY=");
    Serial.println(humidity);
  }
}

void setRGB(int r, int g, int b) {
  analogWrite(RGB_R, r);
  analogWrite(RGB_G, g);
  analogWrite(RGB_B, b);
}

void readDHT11() {
  uint8_t data[5] = {0, 0, 0, 0, 0};
  uint8_t cnt = 7;
  uint8_t idx = 0;

  pinMode(DHT_PIN, OUTPUT);
  digitalWrite(DHT_PIN, LOW);
  delay(18);
  digitalWrite(DHT_PIN, HIGH);
  delayMicroseconds(40);
  pinMode(DHT_PIN, INPUT);

  unsigned int loopCnt = 10000;
  while(digitalRead(DHT_PIN) == LOW) if(loopCnt-- == 0) return;
  
  loopCnt = 10000;
  while(digitalRead(DHT_PIN) == HIGH) if(loopCnt-- == 0) return;

  for (int i = 0; i < 40; i++) {
    loopCnt = 10000;
    while(digitalRead(DHT_PIN) == LOW) if(loopCnt-- == 0) return;
    
    unsigned long t = micros();
    
    loopCnt = 10000;
    while(digitalRead(DHT_PIN) == HIGH) if(loopCnt-- == 0) return;
    
    if ((micros() - t) > 40) data[idx] |= (1 << cnt);
    if (cnt == 0) {
      cnt = 7;
      idx++;
    } else cnt--;
  }

  humidity = data[0];
  temperature = data[2];
}