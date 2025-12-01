class AutoController:
    def __init__(self, device_controller):
        self.device = device_controller

    def run(self, sensor_data):
        """
        자동 제어 알고리즘 뼈대
        """
        temp = sensor_data.get("temperature")
        hum = sensor_data.get("humidity")

        # TODO: 실제 조건식 추가
        # 예: if temp >= 28: self.device.execute("AC_ON")

        pass
