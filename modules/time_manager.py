# modules/time_manager.py 수정본 (시작시 ON, 종료시 OFF)

from datetime import datetime
import time

class TimeManager:
    def __init__(self, device_controller):
        self.device = device_controller
        self.initialized = False
    
    def update(self):
        """프로그램 시작시 LED ON (한 번만)"""
        if not self.initialized:
            self.device.led_on()
            self.initialized = True
    
    def shutdown(self):
        """프로그램 종료시 LED OFF"""
        self.device.led_off()
    
    def is_day_mode(self):
        """낮 모드 확인"""
        current_hour = datetime.now().hour
        return 6 <= current_hour < 18