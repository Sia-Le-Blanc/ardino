import time
from modules.serial_controller import SerialController
from modules.voice_recognition import VoiceRecognizer
from modules.device_controller import DeviceController
from modules.sensor_manager import SensorManager
from modules.automation import Automation
from modules.time_manager import TimeManager

def main():
    print("=== 스마트홈 시스템 시작 ===")
    
    serial = SerialController()
    voice = VoiceRecognizer()
    device = DeviceController(serial)
    sensor = SensorManager(serial)
    automation = Automation(device, sensor)
    time_manager = TimeManager(device)
    
    last_status_time = time.time()
    last_time_update = time.time()
    
    try:
        while True:
            # 1분마다 시간 업데이트
            if time.time() - last_time_update > 60:
                serial.send_time()
                last_time_update = time.time()
            
            # 음성 명령 감지
            if voice.listen_for_trigger():
                print("\n🎤 음성 명령을 말씀하세요...")
                command = voice.recognize_command()
                
                if command:
                    print(f"✓ 인식된 명령: {command}")
                    
                    if command == "LIGHT_ON":
                        device.light_on()
                    elif command == "LIGHT_OFF":
                        device.light_off()
                    elif command == "AC_ON":
                        device.ac_on()
                    elif command == "AC_OFF":
                        device.ac_off()
                    elif command == "HUM_ON":
                        device.hum_on()
                    elif command == "HUM_OFF":
                        device.hum_off()
                    elif command == "LED_ON":
                        device.led_on()
                    elif command == "LED_OFF":
                        device.led_off()
                    elif command == "UNKNOWN":
                        print("❌ 명령을 이해하지 못했습니다.")
            
            # 센서 업데이트
            sensor.update()
            
            # 자동 제어
            automation.update()
            
            # 시간 기반 제어
            time_manager.update()
            
            # 10초마다 상태 출력
            if time.time() - last_status_time > 10:
                temp = sensor.get_temperature()
                hum = sensor.get_humidity()
                states = device.get_states()
                
                print(f"\n📊 온도: {temp}°C | 습도: {hum}% | 에어컨: {states['ac']} | 가습기: {states['hum']}")
                last_status_time = time.time()
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n=== 시스템 종료 ===")
        serial.close()

if __name__ == "__main__":
    main()