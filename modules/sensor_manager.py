class SensorManager:
    def __init__(self, serial_controller):
        self.serial = serial_controller

    def get_sensor_data(self):
        """
        Arduino에서 온도/습도 받아오기
        """
        # TODO: 실제 데이터 파싱
        return {
            "temperature": None,
            "humidity": None
        }
