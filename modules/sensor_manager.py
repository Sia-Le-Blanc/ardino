# modules/sensor_manager.py

import time

class SensorManager:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.temperature = None
        self.humidity = None
    
    def update(self):
        """센서 데이터 업데이트"""
        # 온도 요청
        self.serial.request_temperature()
        response = self.serial.get_response()
        if "TEMPERATURE=" in response:
            try:
                self.temperature = float(response.split("=")[1])
            except:
                pass
        
        # 습도 요청
        self.serial.request_humidity()
        response = self.serial.get_response()
        if "HUMIDITY=" in response:
            try:
                self.humidity = float(response.split("=")[1])
            except:
                pass
    
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