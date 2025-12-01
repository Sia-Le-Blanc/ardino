import time
from datetime import datetime

class TimeManager:
    def __init__(self, device_controller=None):
        self.device = device_controller
        self.mode = None  # "DAY" or "NIGHT"
        self.last_mode = None
        self.led_blinking = False
        
        # 시간대 설정
        self.DAY_START = 6    # 오전 6시부터 낮
        self.NIGHT_START = 18 # 오후 6시부터 밤

    def update(self):
        """
        시간대를 기반으로 낮/밤 모드를 결정하고 LED 제어
        """
        current_hour = time.localtime().tm_hour
        
        # 모드 판단
        if self.DAY_START <= current_hour < self.NIGHT_START:
            self.mode = "DAY"
        else:
            self.mode = "NIGHT"
        
        # 모드 변경시 LED 제어
        if self.mode != self.last_mode:
            self.handle_mode_change()
            self.last_mode = self.mode
        
        # 밤 모드에서 점멸 처리
        if self.mode == "NIGHT" and self.device:
            self.handle_night_blinking()
            
        return self.mode

    def handle_mode_change(self):
        """
        낮/밤 모드 변경시 처리
        """
        current_time = datetime.now().strftime("%H:%M")
        
        if self.mode == "DAY":
            print(f"[TIME] {current_time} - 낮 모드로 전환")
            if self.device:
                self.device.execute("LED_ON")  # 낮에는 점등
                self.led_blinking = False
                
        elif self.mode == "NIGHT":
            print(f"[TIME] {current_time} - 밤 모드로 전환")
            if self.device:
                self.led_blinking = True  # 밤에는 점멸 시작

    def handle_night_blinking(self):
        """
        밤 모드에서 LED 점멸 처리 (1초 간격)
        """
        if not self.led_blinking:
            return
            
        # 현재 초가 짝수면 ON, 홀수면 OFF
        current_second = time.localtime().tm_sec
        
        if current_second % 2 == 0:
            self.device.execute("LED_ON")
        else:
            self.device.execute("LED_OFF")

    def get_current_info(self):
        """
        현재 시간 정보 반환
        """
        now = datetime.now()
        return {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": self.mode,
            "hour": now.hour,
            "is_day": self.is_day(),
            "is_night": self.is_night()
        }

    def is_day(self):
        """낮인지 확인"""
        return self.mode == "DAY"

    def is_night(self):
        """밤인지 확인"""
        return self.mode == "NIGHT"
    
    def set_time_range(self, day_start=None, night_start=None):
        """
        낮/밤 시간대 설정 변경
        """
        if day_start is not None:
            self.DAY_START = day_start
        if night_start is not None:
            self.NIGHT_START = night_start
            
        print(f"[TIME] 시간대 설정 완료 - 낮: {self.DAY_START}시~{self.NIGHT_START-1}시, 밤: {self.NIGHT_START}시~{self.DAY_START-1}시")

    def get_status(self):
        """
        시간 관리 상태 반환
        """
        info = self.get_current_info()
        return {
            "current_mode": self.mode,
            "current_time": info["current_time"],
            "day_range": f"{self.DAY_START}:00 ~ {self.NIGHT_START-1}:59",
            "night_range": f"{self.NIGHT_START}:00 ~ {self.DAY_START-1}:59",
            "led_blinking": self.led_blinking if self.mode == "NIGHT" else False
        }