class DeviceController:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.device_status = {
            "light": "UNKNOWN",
            "humidifier": "OFF", 
            "ac": "OFF",
            "led": "OFF"
        }

    def execute(self, command):
        """
        조명/가습기/에어컨 제어 명령 실행
        """
        if command == "LIGHT_ON":
            self.serial.send("LIGHT_ON")
            self.device_status["light"] = "ON"
            print("[DEVICE] 조명 켜짐")
            
        elif command == "LIGHT_OFF":
            self.serial.send("LIGHT_OFF")
            self.device_status["light"] = "OFF"
            print("[DEVICE] 조명 꺼짐")
            
        elif command == "HUM_ON":
            self.serial.send("HUM_ON")
            self.device_status["humidifier"] = "ON"
            print("[DEVICE] 가습기 켜짐")
            
        elif command == "HUM_OFF":
            self.serial.send("HUM_OFF")
            self.device_status["humidifier"] = "OFF"
            print("[DEVICE] 가습기 꺼짐")
            
        elif command == "AC_ON":
            self.serial.send("AC_ON")
            self.device_status["ac"] = "ON"
            print("[DEVICE] 에어컨 켜짐")
            
        elif command == "AC_OFF":
            self.serial.send("AC_OFF")
            self.device_status["ac"] = "OFF"
            print("[DEVICE] 에어컨 꺼짐")
            
        elif command == "LED_ON":
            self.serial.send("LED_ON")
            self.device_status["led"] = "ON"
            
        elif command == "LED_OFF":
            self.serial.send("LED_OFF")
            self.device_status["led"] = "OFF"
            
        else:
            print(f"[DEVICE] 알 수 없는 명령: {command}")

    def get_status(self):
        """
        현재 기기 상태 반환
        """
        return self.device_status.copy()
    
    def manual_control(self, device, action):
        """
        수동 제어 (테스트용)
        """
        command = f"{device.upper()}_{action.upper()}"
        self.execute(command)