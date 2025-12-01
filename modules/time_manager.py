# modules/time_manager.py

from datetime import datetime

class TimeManager:
    def __init__(self, device_controller):
        self.device = device_controller
        self.last_led_state = None
    
    def update(self):
        """시간에 따른 LED 제어"""
        current_hour = datetime.now().hour
        
        # 낮 모드: 6시 ~ 18시
        if 6 <= current_hour < 18:
            if self.last_led_state != "day":
                self.device.led_on()
                self.last_led_state = "day"
        
        # 밤 모드: 18시 ~ 6시 (점멸)
        else:
            current_second = datetime.now().second
            
            if current_second % 2 == 0:
                if self.last_led_state != "night_on":
                    self.device.led_on()
                    self.last_led_state = "night_on"
            else:
                if self.last_led_state != "night_off":
                    self.device.led_off()
                    self.last_led_state = "night_off"
    
    def is_day_mode(self):
        """낮 모드 확인"""
        current_hour = datetime.now().hour
        return 6 <= current_hour < 18