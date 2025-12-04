# modules/automation.py 수정본

import time

class Automation:
    def __init__(self, device_controller, sensor_manager):
        self.device = device_controller
        self.sensor = sensor_manager
        self.last_actions = {
            "humidifier": None,
            "ac": None
        }
        self.manual_override = {
            "humidifier": False,
            "ac": False
        }
        self.manual_override_time = {
            "humidifier": 0,
            "ac": 0
        }
        
        # 제어 임계값
        self.HUMIDITY_LOW = 40.0
        self.HUMIDITY_HIGH = 60.0
        self.TEMP_HIGH = 28.0
        self.TEMP_LOW = 26.0
        
        # 수동 제어 후 자동 복귀 시간 (초)
        self.MANUAL_OVERRIDE_DURATION = 300  # 5분
    
    def set_manual_override(self, device_type):
        """수동 제어 활성화"""
        if device_type in ["ac", "humidifier"]:
            self.manual_override[device_type] = True
            self.manual_override_time[device_type] = time.time()
            print(f"[AUTO] {device_type} 수동 제어 모드 (5분간 자동 제어 중지)")
    
    def check_manual_override(self, device_type):
        """수동 제어 시간 만료 확인"""
        if self.manual_override[device_type]:
            elapsed = time.time() - self.manual_override_time[device_type]
            if elapsed > self.MANUAL_OVERRIDE_DURATION:
                self.manual_override[device_type] = False
                print(f"[AUTO] {device_type} 자동 제어 모드 복귀")
    
    def update(self):
        """자동 제어 실행"""
        # 센서 데이터 유효성 확인
        if not self.sensor.is_data_valid():
            return
        
        sensor_data = self.sensor.get_data()
        temp = sensor_data.get("temperature")
        hum = sensor_data.get("humidity")
        
        if temp is None or hum is None:
            return
        
        try:
            # 수동 제어 만료 확인
            self.check_manual_override("humidifier")
            self.check_manual_override("ac")
            
            # 습도 기반 가습기 제어 (수동 제어 중이 아닐 때만)
            if not self.manual_override["humidifier"]:
                if hum <= self.HUMIDITY_LOW:
                    if self.last_actions["humidifier"] != "ON":
                        print(f"[AUTO] 습도 {hum}% ≤ {self.HUMIDITY_LOW}% → 가습기 ON")
                        self.device.hum_on()
                        self.last_actions["humidifier"] = "ON"
                elif hum >= self.HUMIDITY_HIGH:
                    if self.last_actions["humidifier"] != "OFF":
                        print(f"[AUTO] 습도 {hum}% ≥ {self.HUMIDITY_HIGH}% → 가습기 OFF")
                        self.device.hum_off()
                        self.last_actions["humidifier"] = "OFF"
            
            # 온도 기반 에어컨 제어 (수동 제어 중이 아닐 때만)
            if not self.manual_override["ac"]:
                if temp >= self.TEMP_HIGH:
                    if self.last_actions["ac"] != "ON":
                        print(f"[AUTO] 온도 {temp}°C ≥ {self.TEMP_HIGH}°C → 에어컨 ON")
                        self.device.ac_on()
                        self.last_actions["ac"] = "ON"
                elif temp <= self.TEMP_LOW:
                    if self.last_actions["ac"] != "OFF":
                        print(f"[AUTO] 온도 {temp}°C ≤ {self.TEMP_LOW}°C → 에어컨 OFF")
                        self.device.ac_off()
                        self.last_actions["ac"] = "OFF"
                        
        except Exception as e:
            print(f"❌ 자동 제어 오류: {e}")