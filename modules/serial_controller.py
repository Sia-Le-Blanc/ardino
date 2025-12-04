# modules/serial_controller.py 수정본 (큐 쌓임 방지)

import serial
import serial.tools.list_ports
import time
import threading
from datetime import datetime
from queue import Queue

class SerialController:
    def __init__(self, port=None):
        self.serial = None
        self.test_mode = False
        self.response_queue = Queue()
        self.is_connected = False
        
        if port:
            try:
                self.serial = serial.Serial(port, baudrate=9600, timeout=1.0)
                time.sleep(2.0)
                self.is_connected = True
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
                        self.is_connected = True
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
        """스레드 안전한 데이터 읽기"""
        while True:
            try:
                if self.serial and self.is_connected:
                    read_data = self.serial.readline()
                    if read_data:
                        decoded = read_data.decode().strip()
                        # 센서 응답만 큐에 저장
                        if "TEMPERATURE=" in decoded or "HUMIDITY=" in decoded:
                            self.response_queue.put(decoded)
            except serial.SerialException as e:
                print(f"✗ 시리얼 연결 끊김: {e}")
                self.is_connected = False
                break
            except Exception as e:
                print(f"✗ 읽기 오류: {e}")
                time.sleep(0.1)
    
    def send_command(self, command):
        """명령 전송"""
        if self.test_mode:
            print(f"[TEST] 전송: {command}")
        else:
            if self.serial and self.is_connected:
                try:
                    self.serial.write(f"{command}\n".encode())
                except serial.SerialException as e:
                    print(f"✗ 전송 실패: {e}")
                    self.is_connected = False
                except Exception as e:
                    print(f"✗ 명령 전송 오류: {e}")
    
    def send_rgb(self, r, g, b):
        self.send_command(f"RGB={r},{g},{b}")
    
    def send_servo(self, degree):
        self.send_command(f"SERVO={degree}")
    
    def send_buzzer(self, freq):
        self.send_command(f"BUZZER={freq}")
    
    def send_time(self):
        """현재 시간을 TM1637에 전송"""
        now = datetime.now()
        time_value = now.hour * 100 + now.minute
        self.send_command(f"TIME={time_value}")
    
    def request_temperature(self):
        self.send_command("TEMPERATURE=?")
    
    def request_humidity(self):
        self.send_command("HUMIDITY=?")
    
    def get_response(self):
        """큐에서 응답 가져오기 (최신 데이터 우선)"""
        try:
            # 큐에 쌓인 오래된 데이터 모두 버리고 최신만 가져오기
            response = None
            while not self.response_queue.empty():
                response = self.response_queue.get()
            return response
        except Exception as e:
            print(f"✗ 응답 읽기 오류: {e}")
        return None
    
    def close(self):
        """시리얼 연결 종료"""
        if self.serial:
            try:
                self.is_connected = False
                self.serial.close()
                print("✓ 시리얼 연결 종료")
            except Exception as e:
                print(f"✗ 종료 오류: {e}")