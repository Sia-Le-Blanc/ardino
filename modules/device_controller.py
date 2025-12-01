# modules/device_controller.py

class DeviceController:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.ac_state = False
        self.hum_state = False
    
    def light_on(self):
        """조명 켜기 - 서보모터 90도"""
        self.serial.send_servo(90)
        self.serial.send_buzzer(523)  # 도 음
        print("💡 조명 ON")
    
    def light_off(self):
        """조명 끄기 - 서보모터 0도"""
        self.serial.send_servo(0)
        self.serial.send_buzzer(0)
        print("💡 조명 OFF")
    
    def ac_on(self):
        """에어컨 켜기 - RGB 빨강"""
        self.serial.send_rgb(255, 0, 0)
        self.ac_state = True
        print("❄️ 에어컨 ON")
    
    def ac_off(self):
        """에어컨 끄기"""
        self._update_rgb()
        self.ac_state = False
        print("❄️ 에어컨 OFF")
    
    def hum_on(self):
        """가습기 켜기 - RGB 초록"""
        self.serial.send_rgb(0, 255, 0)
        self.hum_state = True
        print("💧 가습기 ON")
    
    def hum_off(self):
        """가습기 끄기"""
        self._update_rgb()
        self.hum_state = False
        print("💧 가습기 OFF")
    
    def led_on(self):
        """상태등 켜기 - RGB 파랑"""
        self.serial.send_rgb(0, 0, 255)
        print("🔵 상태등 ON")
    
    def led_off(self):
        """상태등 끄기"""
        self._update_rgb()
        print("🔵 상태등 OFF")
    
    def _update_rgb(self):
        """현재 상태에 맞게 RGB 업데이트"""
        r = 255 if self.ac_state else 0
        g = 255 if self.hum_state else 0
        self.serial.send_rgb(r, g, 0)
    
    def get_states(self):
        """현재 상태 반환"""
        return {
            'ac': self.ac_state,
            'hum': self.hum_state
        }