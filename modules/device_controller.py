class DeviceController:
    def __init__(self, serial_controller):
        self.serial = serial_controller

    def execute(self, command):
        """
        조명/가습기/에어컨 제어 명령 실행
        """
        if command == "LIGHT_ON":
            self.serial.send("LIGHT_ON")
        elif command == "LIGHT_OFF":
            self.serial.send("LIGHT_OFF")
        elif command == "HUMIDIFIER_ON":
            self.serial.send("HUM_ON")
        elif command == "AC_ON":
            self.serial.send("AC_ON")
        else:
            print("[DEVICE] 알 수 없는 명령:", command)
