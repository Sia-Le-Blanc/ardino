from modules.voice_recognition import recognize_voice
from modules.command_parser import parse_command
from modules.serial_controller import SerialController
from modules.sensor_manager import SensorManager
from modules.device_controller import DeviceController
from modules.automation import AutoController
from modules.time_manager import TimeManager

def main():
    print("[SYSTEM] 내 손안의 나의 방 - 시스템 시작")

    serial = SerialController()
    device = DeviceController(serial)
    sensor = SensorManager(serial)
    auto = AutoController(device)
    time_mgr = TimeManager()

    while True:
        # 1) 음성 인식
        text = recognize_voice()
        if text:
            print(f"[VOICE] 인식된 명령: {text}")

            # 2) 명령 파싱
            command = parse_command(text)
            print(f"[COMMAND] 변환된 명령: {command}")

            # 3) 명령 실행
            device.execute(command)

        # 4) 센서 데이터 수신
        data = sensor.get_sensor_data()
        print(f"[SENSOR] {data}")

        # 5) 자동 제어
        auto.run(data)

        # 6) 시간 제어
        time_mgr.update()

if __name__ == "__main__":
    main()
