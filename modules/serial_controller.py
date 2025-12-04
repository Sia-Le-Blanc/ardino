# modules/serial_controller.py

import serial
import serial.tools.list_ports
import time
import threading
from datetime import datetime

class SerialController:
    def __init__(self, port=None):
        self.serial = None
        self.test_mode = False
        self.receive_data = ""
        
        if port:
            try:
                self.serial = serial.Serial(port, baudrate=9600, timeout=1.0)
                time.sleep(2.0)
                print(f"✓ {port} 포트에 연결되었습니다.")
                
                t1 = threading.Thread(target=self._read_thread)
                t1.daemon = True
                t1.start()
            except Exception as e:
                print(f"✗ 시리얼 연결 실패: {e}")
                print("→ 테스트 모드로 전환합니다.")
                self.test_mode = True
        else:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                if 'Arduino Uno' in p.description:
                    try:
                        self.serial = serial.Serial(p.device, baudrate=9600, timeout=1.0)
                        time.sleep(2.0)
                        print(f"✓ {p.device} 포트에 연결되었습니다.")
                        
                        t1 = threading.Thread(target=self._read_thread)
                        t1.daemon = True
                        t1.start()
                        return
                    except:
                        pass
            
            print("✗ 아두이노를 찾을 수 없습니다.")
            print("→ 테스트 모드로 전환합니다.")
            self.test_mode = True
    
    def _read_thread(self):
        while True:
            if self.serial:
                read_data = self.serial.readline()
                if read_data:
                    self.receive_data = read_data.decode().strip()
    
    def send_command(self, command):
        if self.test_mode:
            print(f"[TEST] 전송: {command}")
        else:
            if self.serial:
                self.serial.write(f"{command}\n".encode())
    
    def send_rgb(self, r, g, b):
        self.send_command(f"RGB={r},{g},{b}")
    
    def send_servo(self, degree):
        self.send_command(f"SERVO={degree}")
    
    def send_buzzer(self, freq):
        self.send_command(f"BUZZER={freq}")
    
    def send_time(self):
        """현재 시간을 TM1637에 전송"""
        now = datetime.now()
        time_value = now.hour * 100 + now.minute  # 예: 14:30 → 1430
        self.send_command(f"TIME={time_value}")
    
    def request_temperature(self):
        self.send_command("TEMPERATURE=?")
        time.sleep(0.2)
    
    def request_humidity(self):
        self.send_command("HUMIDITY=?")
        time.sleep(0.2)
    
    def get_response(self):
        data = self.receive_data
        self.receive_data = ""
        return data
    
    def close(self):
        if self.serial:
            self.serial.close()