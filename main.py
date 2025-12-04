# main.py 전체 코드

import time
import threading
from modules.serial_controller import SerialController
from modules.voice_recognition import VoiceRecognizer
from modules.device_controller import DeviceController
from modules.sensor_manager import SensorManager
from modules.automation import Automation
from modules.time_manager import TimeManager

class VoiceThread(threading.Thread):
    def __init__(self, voice, device, automation):
        super().__init__()
        self.voice = voice
        self.device = device
        self.automation = automation
        self.daemon = True
        self.running = True
    
    def run(self):
        """음성 인식 스레드"""
        while self.running:
            try:
                if self.voice.listen_for_trigger():
                    print("\n🎤 음성 명령을 말씀하세요...")
                    command = self.voice.recognize_command()
                    
                    if command:
                        print(f"✓ 인식된 명령: {command}")
                        self.execute_command(command)
            except Exception as e:
                print(f"❌ 음성 인식 오류: {e}")
    
    def execute_command(self, command):
        """명령 실행"""
        if command == "LIGHT_ON":
            self.device.light_on()
        elif command == "LIGHT_OFF":
            self.device.light_off()
        elif command == "AC_ON":
            self.device.ac_on()
            self.automation.set_manual_override("ac")
        elif command == "AC_OFF":
            self.device.ac_off()
            self.automation.set_manual_override("ac")
        elif command == "HUM_ON":
            self.device.hum_on()
            self.automation.set_manual_override("humidifier")
        elif command == "HUM_OFF":
            self.device.hum_off()
            self.automation.set_manual_override("humidifier")
        elif command == "LED_ON":
            self.device.led_on()
        elif command == "LED_OFF":
            self.device.led_off()
        elif command == "UNKNOWN":
            print("❌ 명령을 이해하지 못했습니다.")
    
    def stop(self):
        self.running = False

def main():
    print("=== 스마트홈 시스템 시작 ===")
    
    serial = SerialController()
    voice = VoiceRecognizer()
    device = DeviceController(serial)
    sensor = SensorManager(serial)
    automation = Automation(device, sensor)
    time_manager = TimeManager(device)
    
    # 음성 인식 스레드 시작
    voice_thread = VoiceThread(voice, device, automation)
    voice_thread.start()
    
    last_sensor_update = 0
    last_automation_update = 0
    last_time_update = 0
    last_status_print = 0
    
    SENSOR_INTERVAL = 2.0
    AUTOMATION_INTERVAL = 3.0
    TIME_UPDATE_INTERVAL = 60.0
    STATUS_PRINT_INTERVAL = 10.0
    
    try:
        while True:
            current_time = time.time()
            
            # 1분마다 시간 업데이트
            if current_time - last_time_update >= TIME_UPDATE_INTERVAL:
                serial.send_time()
                last_time_update = current_time
            
            # 2초마다 센서 업데이트
            if current_time - last_sensor_update >= SENSOR_INTERVAL:
                sensor.update()
                last_sensor_update = current_time
            
            # 3초마다 자동 제어
            if current_time - last_automation_update >= AUTOMATION_INTERVAL:
                automation.update()
                last_automation_update = current_time
            
            # 매 루프마다 시간 기반 제어
            time_manager.update()
            
            # 10초마다 상태 출력
            if current_time - last_status_print >= STATUS_PRINT_INTERVAL:
                temp = sensor.get_temperature()
                hum = sensor.get_humidity()
                states = device.get_states()
                
                print(f"\n📊 온도: {temp}°C | 습도: {hum}% | 에어컨: {states['ac']} | 가습기: {states['hum']} | LED: {states['led']}")
                last_status_print = current_time
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n=== 시스템 종료 ===")
        time_manager.shutdown()  # 추가
        voice_thread.stop()
        serial.close()

if __name__ == "__main__":
    main()