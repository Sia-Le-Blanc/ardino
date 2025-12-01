from modules.voice_recognition import recognize_voice
from modules.serial_controller import SerialController
from modules.sensor_manager import SensorManager
from modules.device_controller import DeviceController
from modules.automation import AutoController
from modules.time_manager import TimeManager
import time

def main():
    print("=" * 50)
    print("🏠 내 손안의 나의 방 - 스마트홈 시스템")
    print("=" * 50)
    print("[SYSTEM] 시스템 시작중...")

    try:
        # 시리얼 포트 설정 (실제 사용시 포트 지정 필요)
        # 예: serial = SerialController("COM3") 또는 serial = SerialController("/dev/ttyUSB0")
        serial = SerialController()  # 테스트 모드
        
        # 모듈 초기화
        device = DeviceController(serial)
        sensor = SensorManager(serial)
        auto = AutoController(device)
        time_mgr = TimeManager(device)
        
        print("[SYSTEM] ✅ 모든 모듈 초기화 완료")
        print("[SYSTEM] 💬 '두노야' 명령을 기다리는 중...")
        print("-" * 50)

        while True:
            try:
                # 1) 음성 인식 (두노야 트리거 + 명령)
                command = recognize_voice()
                if command and command != "UNKNOWN":
                    print(f"[VOICE] ✅ 명령 실행: {command}")
                    device.execute(command)
                    print("-" * 30)

                # 2) 센서 데이터 수신 및 자동 제어
                sensor_data = sensor.get_sensor_data()
                if sensor.is_data_valid():
                    auto.run(sensor_data)

                # 3) 시간 기반 제어
                time_mgr.update()

                # 4) 상태 출력 (10초마다)
                if int(time.time()) % 10 == 0:
                    print_status(sensor, device, auto, time_mgr)

                time.sleep(0.5)  # CPU 사용량 최적화

            except KeyboardInterrupt:
                print("\n[SYSTEM] 사용자에 의해 종료되었습니다.")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(1)

    except Exception as e:
        print(f"[INIT ERROR] 초기화 실패: {e}")
    
    finally:
        if 'serial' in locals():
            serial.close()
        print("[SYSTEM] 시스템 종료")

def print_status(sensor, device, auto, time_mgr):
    """
    시스템 상태 출력
    """
    temp = sensor.get_temperature()
    hum = sensor.get_humidity()
    devices = device.get_status()
    time_info = time_mgr.get_status()
    
    print("\n📊 [시스템 상태]")
    print(f"🌡️  온도: {temp if temp else 'N/A'}°C")
    print(f"💧 습도: {hum if hum else 'N/A'}%")
    print(f"💡 조명: {devices['light']} | 💨 가습기: {devices['humidifier']} | ❄️  에어컨: {devices['ac']}")
    print(f"🕐 시간: {time_info['current_mode']} 모드 ({time_info['current_time'][:16]})")
    print("-" * 50)

def manual_test():
    """
    수동 테스트 모드
    """
    print("🔧 [수동 테스트 모드]")
    serial = SerialController()
    device = DeviceController(serial)
    
    while True:
        print("\n명령어 입력 (예: LIGHT_ON, HUM_OFF, quit):")
        cmd = input("> ").strip().upper()
        
        if cmd == "QUIT":
            break
        
        device.execute(cmd)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        manual_test()
    else:
        main()