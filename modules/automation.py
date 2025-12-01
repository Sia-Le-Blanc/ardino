class AutoController:
    def __init__(self, device_controller):
        self.device = device_controller
        self.last_actions = {
            "humidifier": None,
            "ac": None
        }
        
        # 제어 임계값 설정
        self.HUMIDITY_LOW = 40.0    # 습도 40% 이하면 가습기 ON
        self.HUMIDITY_HIGH = 70.0   # 습도 70% 이상이면 가습기 OFF
        self.TEMP_HIGH = 28.0       # 온도 28도 이상이면 에어컨 ON
        self.TEMP_LOW = 24.0        # 온도 24도 이하면 에어컨 OFF

    def run(self, sensor_data):
        """
        자동 제어 알고리즘 실행
        """
        temp = sensor_data.get("temperature")
        hum = sensor_data.get("humidity")
        
        if temp is None or hum is None:
            print("[AUTO] 센서 데이터 없음 - 자동 제어 스킵")
            return
        
        print(f"[AUTO] 현재 상태 - 온도: {temp}°C, 습도: {hum}%")
        
        # 습도 기반 가습기 제어
        self.control_humidifier(hum)
        
        # 온도 기반 에어컨 제어  
        self.control_airconditioner(temp)
    
    def control_humidifier(self, humidity):
        """
        습도 기반 가습기 자동 제어
        """
        if humidity <= self.HUMIDITY_LOW:
            if self.last_actions["humidifier"] != "ON":
                print(f"[AUTO] 습도 {humidity}% ≤ {self.HUMIDITY_LOW}% → 가습기 ON")
                self.device.execute("HUM_ON")
                self.last_actions["humidifier"] = "ON"
                
        elif humidity >= self.HUMIDITY_HIGH:
            if self.last_actions["humidifier"] != "OFF":
                print(f"[AUTO] 습도 {humidity}% ≥ {self.HUMIDITY_HIGH}% → 가습기 OFF")
                self.device.execute("HUM_OFF")
                self.last_actions["humidifier"] = "OFF"
        else:
            # 중간 범위에서는 현재 상태 유지
            pass
    
    def control_airconditioner(self, temperature):
        """
        온도 기반 에어컨 자동 제어
        """
        if temperature >= self.TEMP_HIGH:
            if self.last_actions["ac"] != "ON":
                print(f"[AUTO] 온도 {temperature}°C ≥ {self.TEMP_HIGH}°C → 에어컨 ON")
                self.device.execute("AC_ON")
                self.last_actions["ac"] = "ON"
                
        elif temperature <= self.TEMP_LOW:
            if self.last_actions["ac"] != "OFF":
                print(f"[AUTO] 온도 {temperature}°C ≤ {self.TEMP_LOW}°C → 에어컨 OFF")
                self.device.execute("AC_OFF")
                self.last_actions["ac"] = "OFF"
        else:
            # 중간 범위에서는 현재 상태 유지
            pass
    
    def set_thresholds(self, hum_low=None, hum_high=None, temp_low=None, temp_high=None):
        """
        임계값 설정 변경
        """
        if hum_low is not None:
            self.HUMIDITY_LOW = hum_low
        if hum_high is not None:
            self.HUMIDITY_HIGH = hum_high
        if temp_low is not None:
            self.TEMP_LOW = temp_low
        if temp_high is not None:
            self.TEMP_HIGH = temp_high
            
        print(f"[AUTO] 임계값 설정 완료 - 습도: {self.HUMIDITY_LOW}~{self.HUMIDITY_HIGH}%, 온도: {self.TEMP_LOW}~{self.TEMP_HIGH}°C")
    
    def get_status(self):
        """
        현재 자동 제어 상태 반환
        """
        return {
            "humidifier_status": self.last_actions["humidifier"],
            "ac_status": self.last_actions["ac"],
            "thresholds": {
                "humidity_range": f"{self.HUMIDITY_LOW}~{self.HUMIDITY_HIGH}%",
                "temperature_range": f"{self.TEMP_LOW}~{self.TEMP_HIGH}°C"
            }
        }