import serial
import time

class SerialController:
    def __init__(self, port=None, baud=9600, timeout=1):
        """
        Arduino와의 시리얼 통신을 초기화하는 모듈
        실제 포트 연결이 없어도 발표용으로 안전하게 동작하도록 구현됨
        """
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None

        try:
            if port:
                self.ser = serial.Serial(port, baud, timeout=timeout)
                time.sleep(2)  # 아두이노 초기 리셋 대기
                print(f"[SERIAL] Connected to {port} at {baud}bps")
            else:
                # 포트 미지정 시 발표/개발 테스트용 모드
                print("[SERIAL] 포트 미지정 → 테스트 모드로 실행됩니다.")
        except Exception as e:
            print("[SERIAL ERROR] 연결 실패:", e)
            self.ser = None

    def send(self, msg: str):
        """
        Python → Arduino 데이터 전송
        """
        if self.ser is None:
            print(f"[SERIAL SEND-TEST] '{msg}' (실제 전송 없음)")
            return

        try:
            full_msg = (msg + "\n").encode("utf-8")
            self.ser.write(full_msg)
            print(f"[SERIAL SEND] '{msg}' 전송 완료")
        except Exception as e:
            print("[SERIAL SEND ERROR]", e)

    def receive(self):
        """
        Arduino → Python 데이터 수신
        """
        if self.ser is None:
            # 발표용: 센서 데이터 없는 경우
            return None

        try:
            if self.ser.in_waiting:
                line = self.ser.readline().decode("utf-8").strip()
                return line
        except Exception as e:
            print("[SERIAL RECEIVE ERROR]", e)
        return None

    def close(self):
        """
        시리얼 연결 종료
        """
        if self.ser:
            self.ser.close()
            print("[SERIAL] 연결 종료")
