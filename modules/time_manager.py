# modules/time_manager.py 수정본

from datetime import datetime
import time

class TimeManager:
    def __init__(self, device_controller):
        self.device = device_controller
        self.last_led_state = None
        self.last_blink_time = 0
        self.blink_interval = 1.0  # 1초마다 깜빡임
    
    def update(self):
        """시간에 따른 LED 제어"""
        current_hour = datetime.now().hour
        current_time = time.time()
        
        # 낮 모드: 6시 ~ 18시
        if 6 <= current_hour < 18:
            if self.last_led_state != "day":
                self.device.led_on()
                self.last_led_state = "day"
        
        # 밤 모드: 18시 ~ 6시 (점멸)
        else:
            # 1초마다 한 번만 토글
            if current_time - self.last_blink_time >= self.blink_interval:
                if self.last_led_state == "night_on":
                    self.device.led_off()
                    self.last_led_state = "night_off"
                else:
                    self.device.led_on()
                    self.last_led_state = "night_on"
                
                self.last_blink_time = current_time
    
    def is_day_mode(self):
        """낮 모드 확인"""
        current_hour = datetime.now().hour
        return 6 <= current_hour < 18