# modules/sensor_manager.py (실습 코드 방식)

import time

class SensorManager:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.temperature = None
        self.humidity = None
        self.error_count = 0
        self.max_errors = 5
    
    def update(self):
        """센서 데이터 업데이트 (실습 코드 방식)"""
        try:
            # 온도 요청
            self.serial.request_temperature()
            time.sleep(0.2)
            
            # 응답 확인
            response = self.serial.get_response()
            if response and "TEMPERATURE=" in response:
                try:
                    temp_str = response.split("=")[1].strip()
                    temp = float(temp_str)
                    if -50 <= temp <= 100:
                        self.temperature = temp
                        self.error_count = 0
                        print(f"온도: {temp}°C")
                except (ValueError, IndexError) as e:
                    print(f"⚠️ 온도 파싱 실패: {response} | {e}")
            
            # 습도 요청
            self.serial.request_humidity()
            time.sleep(0.2)
            
            # 응답 확인
            response = self.serial.get_response()
            if response and "HUMIDITY=" in response:
                try:
                    hum_str = response.split("=")[1].strip()
                    hum = float(hum_str)
                    if 0 <= hum <= 100:
                        self.humidity = hum
                        self.error_count = 0
                        print(f"습도: {hum}%")
                except (ValueError, IndexError) as e:
                    print(f"⚠️ 습도 파싱 실패: {response} | {e}")
                    
        except Exception as e:
            self.error_count += 1
            print(f"❌ 센서 업데이트 오류: {e}")
    
    def get_temperature(self):
        return self.temperature
    
    def get_humidity(self):
        return self.humidity
    
    def get_data(self):
        return {
            'temperature': self.temperature,
            'humidity': self.humidity
        }
    
    def is_data_valid(self):
        return self.temperature is not None and self.humidity is not None