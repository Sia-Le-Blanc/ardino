# modules/sensor_manager.py 수정본 (DHT11 타이밍 개선)

import time

class SensorManager:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.temperature = None
        self.humidity = None
        self.error_count = 0
        self.max_errors = 5
        self.last_read_time = 0
        self.min_read_interval = 2.0  # DHT11 최소 읽기 간격 2초
    
    def update(self):
        """센서 데이터 업데이트 (DHT11 타이밍 준수)"""
        current_time = time.time()
        
        # 최소 읽기 간격 확인
        if current_time - self.last_read_time < self.min_read_interval:
            return
        
        self.last_read_time = current_time
        
        try:
            # 온도 요청 및 응답 대기 (1초)
            self.serial.request_temperature()
            time.sleep(1.0)
            response = self.serial.get_response()
            if response and "TEMPERATURE=" in response:
                try:
                    temp = float(response.split("=")[1])
                    if -50 <= temp <= 100:
                        self.temperature = temp
                        self.error_count = 0
                    else:
                        print(f"⚠️ 비정상 온도 값: {temp}°C")
                except ValueError:
                    self.error_count += 1
                    print(f"⚠️ 온도 파싱 실패: {response}")
            
            # 습도 요청 및 응답 대기 (1초)
            self.serial.request_humidity()
            time.sleep(1.0)
            response = self.serial.get_response()
            if response and "HUMIDITY=" in response:
                try:
                    hum = float(response.split("=")[1])
                    if 0 <= hum <= 100:
                        self.humidity = hum
                        self.error_count = 0
                    else:
                        print(f"⚠️ 비정상 습도 값: {hum}%")
                except ValueError:
                    self.error_count += 1
                    print(f"⚠️ 습도 파싱 실패: {response}")
            
            # 연속 오류 확인
            if self.error_count >= self.max_errors:
                print(f"❌ 센서 연속 오류 {self.error_count}회 - 센서 점검 필요")
                self.error_count = 0
                
        except Exception as e:
            self.error_count += 1
            print(f"❌ 센서 업데이트 오류: {e}")
    
    def get_temperature(self):
        """현재 온도 반환"""
        return self.temperature
    
    def get_humidity(self):
        """현재 습도 반환"""
        return self.humidity
    
    def get_data(self):
        """온도와 습도 반환"""
        return {
            'temperature': self.temperature,
            'humidity': self.humidity
        }
    
    def is_data_valid(self):
        """센서 데이터 유효성 확인"""
        return self.temperature is not None and self.humidity is not None