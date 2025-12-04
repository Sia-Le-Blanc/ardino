# modules/automation.py

class Automation:
    def __init__(self, device_controller, sensor_manager):
        self.device = device_controller
        self.sensor = sensor_manager
        self.last_actions = {
            "humidifier": None,
            "ac": None
        }
        
        # 제어 임계값
        self.HUMIDITY_LOW = 40.0
        self.HUMIDITY_HIGH = 60.0
        self.TEMP_HIGH = 28.0
        self.TEMP_LOW = 26.0
    
    def update(self):
        """자동 제어 실행"""
        sensor_data = self.sensor.get_data()
        temp = sensor_data.get("temperature")
        hum = sensor_data.get("humidity")
        
        if temp is None or hum is None:
            return
        
        # 습도 기반 가습기 제어
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
        
        # 온도 기반 에어컨 제어
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