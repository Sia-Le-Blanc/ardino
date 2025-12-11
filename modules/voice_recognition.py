# modules/voice_recognition.py 수정본

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import speech_recognition as sr
from google import genai
from typing import Optional
import tempfile
import os
import time

GEMINI_API_KEY = "AIzaSyA4z7qP8NJgNOZYw76hJNbVpZIy3s3EShU"


class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000
        self.serial = None

        # Gemini 클라이언트 (v1 기본값 사용, 별도 api_version 강제 X)
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def set_serial(self, serial_controller):
        """시리얼 컨트롤러 설정"""
        self.serial = serial_controller

    def record_audio(self, duration: float):
        """sounddevice로 duration(초)만큼 녹음"""
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        return audio

    def audio_to_text(self, audio_data) -> str:
        """오디오를 텍스트로 변환 (Google Speech Recognition 사용)"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            write(f.name, self.sample_rate, audio_data)

            with sr.AudioFile(f.name) as source:
                audio = self.recognizer.record(source)

        # 임시 파일 삭제
        try:
            os.unlink(f.name)
        except Exception:
            pass

        text = self.recognizer.recognize_google(audio, language="ko-KR")
        return text

    def play_beep(self):
        """아두이노 부저 또는 PC 스피커로 도-미-솔 신호음 출력"""
        frequencies = [523, 659, 784]
        duration = 0.15

        if self.serial:
            # 아두이노 부저 사용
            for freq in frequencies:
                self.serial.send_buzzer(freq)
                time.sleep(duration)
            self.serial.send_buzzer(0)
        else:
            # 시리얼 없으면 PC 스피커
            for freq in frequencies:
                t = np.linspace(0, duration, int(self.sample_rate * duration))
                wave = np.sin(2 * np.pi * freq * t) * 0.3
                sd.play(wave, self.sample_rate)
                sd.wait()

    def listen_for_trigger(self) -> bool:
        """트리거 워드(준호, 주노 등) 감지"""
        try:
            audio = self.record_audio(duration=3)
            text = self.audio_to_text(audio)
            # print(f"[DEBUG] 트리거 인식 텍스트: {text}")

            if any(word in text for word in ["준호", "주노", "존호", "전호"]):
                print(f"✓ 트리거 감지: {text}")
                self.play_beep()
                return True
        except Exception as e:
            print(f"❌ 트리거 인식 실패: {e}")
        return False

    def recognize_command(self) -> Optional[str]:
        """트리거 이후 실제 명령 인식 및 분류"""
        try:
            audio = self.record_audio(duration=5)
            text = self.audio_to_text(audio)
            print(f"✓ 인식된 텍스트: {text}")
            return self.interpret_with_gemini(text)
        except Exception as e:
            print(f"❌ 인식 실패: {e}")
            return None

    def interpret_with_gemini(self, user_command: str) -> str:
        """Gemini로 명령 정교하게 해석 → 9가지 명령 중 하나로 매핑"""

        prompt = f"""
당신은 스마트홈 음성 비서의 명령 분류 전문 AI입니다.
사용자의 한국어 음성 명령을 분석하여, 정확히 하나의 제어 명령으로 분류하세요.

## 중요 원칙
1. 반드시 9가지 명령 중 정확히 하나만 출력
2. 기기명과 동작(켜기/끄기)이 명확해야 함
3. 애매하거나 지원하지 않는 명령은 모두 UNKNOWN
4. 출력은 명령어만 (설명, 이유, 마크다운, 따옴표 일체 금지)

## 가능한 출력 명령 목록
- LIGHT_ON
- LIGHT_OFF
- HUM_ON
- HUM_OFF
- AC_ON
- AC_OFF
- LED_ON
- LED_OFF
- UNKNOWN

## 세부 규칙

### 1. LIGHT_ON
- 대상: "조명", "불", "전등", "라이트", "등", "Light"
- 동작: "켜", "틀어", "켜줘", "켜라", "on", "온"
- 예시: "불 켜줘", "조명 켜", "라이트 온", "등 좀 켜", "전등 틀어줘"
- 단, "상태등", "LED", "엘이디", "표시등"이 함께 나오면 → LED_ON

### 2. LIGHT_OFF
- 대상: "조명", "불", "전등", "라이트", "등", "Light"
- 동작: "꺼", "끄", "꺼줘", "끄기", "off", "오프"
- 예시: "불 꺼", "조명 꺼줘", "라이트 오프", "등 끄기", "전등 꺼"
- 단, "상태등", "LED", "엘이디", "표시등"이 함께 나오면 → LED_OFF

### 3. HUM_ON
- 대상: "가습기", "humidifier"
- 동작: "켜", "틀어", "켜줘", "작동", "on"
- 예시: "가습기 켜", "가습기 틀어", "가습기 작동"
- "습도 올려"처럼 모호하고 "가습기" 언급 없으면 → UNKNOWN

### 4. HUM_OFF
- 대상: "가습기", "humidifier"
- 동작: "꺼", "끄", "정지", "중지", "off"
- 예시: "가습기 꺼", "가습기 끄기", "가습기 정지"

### 5. AC_ON
- 대상: "에어컨", "냉방", "AC", "에어콘", "airconditioner"
- 동작: "켜", "틀어", "켜줘", "작동", "on"
- 또는: "시원하게", "춥게", "온도 낮춰" 등 냉방 의도가 분명한 표현
- 예시: "에어컨 켜", "냉방 틀어", "시원하게 해줘", "춥게 해줘"

### 6. AC_OFF
- 대상: "에어컨", "냉방", "AC"
- 동작: "꺼", "끄", "정지", "off"
- 예시: "에어컨 꺼", "냉방 끄기", "에어컨 정지"

### 7. LED_ON
- 대상: "상태등", "LED", "엘이디", "표시등", "인디케이터"
- 동작: "켜", "틀어", "켜줘", "on"
- 예시: "LED 켜", "상태등 켜줘", "엘이디 온"
- 일반 조명보다 우선

### 8. LED_OFF
- 대상: "상태등", "LED", "엘이디", "표시등"
- 동작: "꺼", "끄", "꺼줘", "off"
- 예시: "LED 꺼", "상태등 끄기"

### 9. UNKNOWN (반드시 UNKNOWN 처리해야 하는 경우)
- 기기명이 전혀 없는 "켜줘", "꺼줘", "작동해줘" 등
- "온도 조절해줘", "쾌적하게 해줘"처럼 추상적인 표현
- TV, 보일러, 커튼, 창문, 스피커, 음악 등 지원하지 않는 기기
- 인사/감사/질문/잡담
- "불 켜고 에어컨도 켜줘" 같은 복합 명령

## 현재 사용자 입력
"{user_command}"

위 규칙에 따라 9가지 명령 중 하나를 고르고,
아래에 그 명령어만 대문자로 한 줄 출력하세요.
"""

        try:
            response = self.client.models.generate_content(
                # ✅ v1에서 공식 지원되는 안정 모델
                model="gemini-2.5-flash",
                contents=prompt
            )

            command = response.text.strip().upper()
            # print(f"[DEBUG] Gemini 응답: {command}")

            valid_commands = [
                "LIGHT_ON", "LIGHT_OFF",
                "HUM_ON", "HUM_OFF",
                "AC_ON", "AC_OFF",
                "LED_ON", "LED_OFF",
                "UNKNOWN",
            ]

            if command in valid_commands:
                return command
            else:
                print(f"[GEMINI] 잘못된 응답: {command} → UNKNOWN 처리")
                return "UNKNOWN"

        except Exception as e:
            print(f"❌ Gemini 오류: {e}")
            return "UNKNOWN"
