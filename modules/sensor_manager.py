import re
from typing import Dict, Optional

class SensorManager:
    def __init__(self, serial_controller):
        self.serial = serial_controller
        self.last_data = {"temperature": None, "humidity": None}
    
    def get_sensor_data(self) -> Dict[str, Optional[float]]:
        """
        Arduino에서 온도/습도 받아오기
        Arduino 형식: "TEMP:25.4,HUM:60.2"
        """
        # 시리얼에서 데이터 수신
        raw_data = self.serial.receive()
        
        if raw_data:
            parsed_data = self.parse_sensor_data(raw_data)
            if parsed_data["temperature"] is not None:
                self.last_data = parsed_data
                return parsed_data
        
        # 새 데이터가 없으면 마지막 데이터 반환
        return self.last_data
    
    def parse_sensor_data(self, data: str) -> Dict[str, Optional[float]]:
        """
        Arduino에서 받은 문자열 파싱
        예: "TEMP:25.4,HUM:60.2" -> {"temperature": 25.4, "humidity": 60.2}
        """
        result = {"temperature": None, "humidity": None}
        
        try:
            # 온도 추출
            temp_match = re.search(r'TEMP:([\d.-]+)', data)
            if temp_match:
                result["temperature"] = float(temp_match.group(1))
            
            # 습도 추출  
            hum_match = re.search(r'HUM:([\d.-]+)', data)
            if hum_match:
                result["humidity"] = float(hum_match.group(1))
                
            print(f"[SENSOR] 파싱 완료 - 온도: {result['temperature']}°C, 습도: {result['humidity']}%")
            
        except ValueError as e:
            print(f"[SENSOR ERROR] 데이터 파싱 실패: {e}")
        except Exception as e:
            print(f"[SENSOR ERROR] {e}")
            
        return result
    
    def is_data_valid(self) -> bool:
        """
        센서 데이터 유효성 검사
        """
        temp = self.last_data["temperature"]
        hum = self.last_data["humidity"]
        
        if temp is None or hum is None:
            return False
            
        # 온도: -10°C ~ 50°C, 습도: 0% ~ 100%
        if not (-10 <= temp <= 50):
            return False
        if not (0 <= hum <= 100):
            return False
            
        return True
    
    def get_temperature(self) -> Optional[float]:
        """온도만 반환"""
        return self.last_data["temperature"]
    
    def get_humidity(self) -> Optional[float]:
        """습도만 반환"""
        return self.last_data["humidity"]