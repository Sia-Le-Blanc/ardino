# modules/device_controller.py 수정본

import threading

class DeviceController:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.ac_state = False
        self.hum_state = False
        self.led_state = False
        self.lock = threading.Lock()
    
    def light_on(self):
        """조명 켜기 - 서보모터 90도"""
        with self.lock:
            self.serial.send_servo(90)
            self.serial.send_buzzer(523)
            print("💡 조명 ON")
    
    def light_off(self):
        """조명 끄기 - 서보모터 0도"""
        with self.lock:
            self.serial.send_servo(0)
            self.serial.send_buzzer(0)
            print("💡 조명 OFF")
    
    def ac_on(self):
        """에어컨 켜기"""
        with self.lock:
            self.ac_state = True
            self._update_rgb()
            print("❄️ 에어컨 ON")
    
    def ac_off(self):
        """에어컨 끄기"""
        with self.lock:
            self.ac_state = False
            self._update_rgb()
            print("❄️ 에어컨 OFF")
    
    def hum_on(self):
        """가습기 켜기"""
        with self.lock:
            self.hum_state = True
            self._update_rgb()
            print("💧 가습기 ON")
    
    def hum_off(self):
        """가습기 끄기"""
        with self.lock:
            self.hum_state = False
            self._update_rgb()
            print("💧 가습기 OFF")
    
    def led_on(self):
        """상태등 켜기"""
        with self.lock:
            self.led_state = True
            self._update_rgb()
            print("🔵 상태등 ON")
    
    def led_off(self):
        """상태등 끄기"""
        with self.lock:
            self.led_state = False
            self._update_rgb()
            print("🔵 상태등 OFF")
    
    def _update_rgb(self):
        """3가지 상태를 모두 반영한 RGB 업데이트 (lock 내부에서만 호출)"""
        r = 255 if self.ac_state else 0
        g = 255 if self.hum_state else 0
        b = 255 if self.led_state else 0
        self.serial.send_rgb(r, g, b)
    
    def get_states(self):
        """현재 상태 반환"""
        with self.lock:
            return {
                'ac': self.ac_state,
                'hum': self.hum_state,
                'led': self.led_state
            }