#include <DHT.h>
#include <Servo.h>

// 핀 정의
#define DHT_PIN 2
#define DHT_TYPE DHT11
#define SERVO_PIN 9
#define RELAY_HUMIDIFIER 7
#define RELAY_AC 8
#define LED_PIN 13

// 객체 초기화
DHT dht(DHT_PIN, DHT_TYPE);
Servo lightServo;

void setup() {
  Serial.begin(9600);
  dht.begin();
  lightServo.attach(SERVO_PIN);
  
  pinMode(RELAY_HUMIDIFIER, OUTPUT);
  pinMode(RELAY_AC, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // 초기 상태 (릴레이 OFF)
  digitalWrite(RELAY_HUMIDIFIER, LOW);
  digitalWrite(RELAY_AC, LOW);
  
  Serial.println("Arduino Ready");
}

void loop() {
  // 센서 데이터 읽기 및 전송
  sendSensorData();
  
  // Python 명령 수신
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    executeCommand(command);
  }
  
  delay(1000);
}

void sendSensorData() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  
  if (!isnan(temp) && !isnan(hum)) {
    Serial.print("TEMP:");
    Serial.print(temp);
    Serial.print(",HUM:");
    Serial.println(hum);
  }
}

void executeCommand(String cmd) {
  if (cmd == "LIGHT_ON") {
    lightServo.write(180); // 스위치 ON 위치
    delay(500);
    lightServo.write(90);  // 중립 위치
  }
  else if (cmd == "LIGHT_OFF") {
    lightServo.write(0);   // 스위치 OFF 위치
    delay(500);
    lightServo.write(90);  // 중립 위치
  }
  else if (cmd == "HUM_ON") {
    digitalWrite(RELAY_HUMIDIFIER, HIGH);
  }
  else if (cmd == "HUM_OFF") {
    digitalWrite(RELAY_HUMIDIFIER, LOW);
  }
  else if (cmd == "AC_ON") {
    digitalWrite(RELAY_AC, HIGH);
  }
  else if (cmd == "AC_OFF") {
    digitalWrite(RELAY_AC, LOW);
  }
  else if (cmd == "LED_ON") {
    digitalWrite(LED_PIN, HIGH);
  }
  else if (cmd == "LED_OFF") {
    digitalWrite(LED_PIN, LOW);
  }
}
