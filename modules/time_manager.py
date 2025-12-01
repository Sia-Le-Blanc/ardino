import time

class TimeManager:
    def __init__(self):
        self.mode = None  # "DAY" or "NIGHT"

    def update(self):
        """
        시간대를 기반으로 낮/밤 모드를 결정하는 모듈
        """
        hour = time.localtime().tm_hour

        if 6 <= hour < 18:
            self.mode = "DAY"
        else:
            self.mode = "NIGHT"

        return self.mode

    def is_day(self):
        return self.mode == "DAY"

    def is_night(self):
        return self.mode == "NIGHT"
