# modules/voice_recognition.py 수정본

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import speech_recognition as sr
import google.generativeai as genai
from typing import Optional
import tempfile
import os

GEMINI_API_KEY = "AIzaSyDkK6vre3W_TMJwKo8XxihUnmGjXc2_X7Q"
genai.configure(api_key=GEMINI_API_KEY)

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.sample_rate = 16000
    
    def record_audio(self, duration):
        """sounddevice로 녹음"""
        audio = sd.rec(int(duration * self.sample_rate), 
                      samplerate=self.sample_rate, 
                      channels=1, 
                      dtype='int16')
        sd.wait()
        return audio
    
    def audio_to_text(self, audio_data):
        """오디오를 텍스트로 변환"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            write(f.name, self.sample_rate, audio_data)
            
            with sr.AudioFile(f.name) as source:
                audio = self.recognizer.record(source)
            
            os.unlink(f.name)
            text = self.recognizer.recognize_google(audio, language='ko-KR')
            return text
    
    def play_beep(self):
        """도-미-솔 신호음 출력"""
        duration = 0.15
        frequencies = [523, 659, 784]
        
        for freq in frequencies:
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            wave = np.sin(2 * np.pi * freq * t) * 0.3
            sd.play(wave, self.sample_rate)
            sd.wait()
    
    def listen_for_trigger(self) -> bool:
        """트리거 워드 감지 (main.py에서 호출)"""
        try:
            audio = self.record_audio(duration=3)
            text = self.audio_to_text(audio)
            
            if any(word in text for word in ["준호", "주노", "존호", "전호"]):
                print(f"✓ 트리거 감지: {text}")
                self.play_beep()
                return True
        except:
            pass
        return False
    
    def recognize_command(self) -> Optional[str]:
        """명령 인식 및 해석 (main.py에서 호출)"""
        try:
            audio = self.record_audio(duration=5)
            text = self.audio_to_text(audio)
            print(f"✓ 인식된 텍스트: {text}")
            return self.interpret_with_gemini(text)
        except Exception as e:
            print(f"❌ 인식 실패: {e}")
            return None
    
    def interpret_with_gemini(self, user_command: str) -> str:
        """Gemini로 명령 정교하게 해석"""
        prompt = f"""
당신은 스마트홈 음성 비서의 명령 분류 전문 AI입니다.
사용자의 한국어 음성 명령을 분석하여, 정확히 하나의 제어 명령으로 분류하세요.

## 중요 원칙
1. 반드시 9가지 명령 중 정확히 하나만 출력
2. 기기명과 동작(켜기/끄기)이 명확해야 함
3. 애매하거나 지원하지 않는 명령은 모두 UNKNOWN
4. 출력은 명령어만 (설명 없음)

## 사용자 입력
"{user_command}"

## 명령어 분류 규칙

### 1. LIGHT_ON
**조건:**
- 대상: "조명", "불", "전등", "라이트", "등", "Light"
- 동작: "켜", "틀어", "켜줘", "켜라", "on", "온"
- 예시: "불 켜줘", "조명 켜", "라이트 온", "등 좀 켜", "전등 틀어줘"
**제외:**
- "상태등", "LED" 언급 시 → LED_ON 우선

### 2. LIGHT_OFF
**조건:**
- 대상: "조명", "불", "전등", "라이트", "등", "Light"
- 동작: "꺼", "끄", "꺼줘", "끄기", "off", "오프"
- 예시: "불 꺼", "조명 꺼줘", "라이트 오프", "등 끄기", "전등 꺼"
**제외:**
- "상태등", "LED" 언급 시 → LED_OFF 우선

### 3. HUM_ON
**조건:**
- 대상: "가습기", "습도", "humidifier"
- 동작: "켜", "틀어", "켜줘", "작동", "on"
- 예시: "가습기 켜", "가습기 틀어", "습도 올려", "가습기 작동"
**주의:**
- "가습기" 명시적 언급 필수
- "습하게" 같은 모호한 표현 → UNKNOWN

### 4. HUM_OFF
**조건:**
- 대상: "가습기", "humidifier"
- 동작: "꺼", "끄", "정지", "중지", "off"
- 예시: "가습기 꺼", "가습기 끄기", "가습기 정지"

### 5. AC_ON
**조건:**
- 대상: "에어컨", "냉방", "AC", "에어콘", "airconditioner"
- 동작: "켜", "틀어", "작동", "on"
- 또는: "시원하게", "춥게", "온도 낮춰" (냉방 의도 명확)
- 예시: "에어컨 켜", "냉방 틀어", "시원하게 해줘", "춥게 해줘"
**제외:**
- 단순 "온도 낮춰" (구체적 수치 없음) → UNKNOWN

### 6. AC_OFF
**조건:**
- 대상: "에어컨", "냉방", "AC"
- 동작: "꺼", "끄", "정지", "off"
- 예시: "에어컨 꺼", "냉방 끄기", "에어컨 정지"

### 7. LED_ON
**조건:**
- 대상: "상태등", "LED", "엘이디", "표시등", "인디케이터"
- 동작: "켜", "틀어", "on"
- 예시: "LED 켜", "상태등 켜줘", "엘이디 온"
**우선순위:**
- "LED"/"상태등" 명시 시 일반 조명보다 우선

### 8. LED_OFF
**조건:**
- 대상: "상태등", "LED", "엘이디", "표시등"
- 동작: "꺼", "끄", "off"
- 예시: "LED 꺼", "상태등 끄기"

### 9. UNKNOWN
**다음의 경우 반드시 UNKNOWN:**

**A. 기기명 없음**
- "켜줘", "틀어줘", "작동해줘" (뭘 켤지 불명확)
- "꺼", "끄기", "정지" (뭘 끌지 불명확)

**B. 동작 불명확**
- "온도 높여", "온도 조절" (구체적 기기 없음)
- "습도 맞춰", "쾌적하게" (추상적)
- "밝게", "어둡게" (조명인지 화면인지 불명확)

**C. 지원하지 않는 기기**
- "TV", "선풍기", "청소기", "보일러", "커튼", "블라인드"
- "난방", "히터", "환풍기", "공기청정기"

**D. 질문/대화**
- "몇 시야?", "날씨 어때?", "온도가 어떻게 돼?"
- "지금 뭐 켜져 있어?", "상태 알려줘"

**E. 인사/감사/잡담**
- "안녕", "고마워", "잘했어", "좋아"
- "알았어", "오케이", "그래", "응"

**F. 모호한 지시**
- "저것 좀", "그거 해줘", "그냥 켜"
- "다 켜", "전부 꺼" (무엇을 가리키는지 불명확)

**G. 복합 명령**
- "불 켜고 에어컨도 켜줘" → UNKNOWN (하나만 처리 가능)
- "다 꺼줘" → UNKNOWN (여러 기기 동시 제어 불가)

## 특수 케이스

### 오인식 대응
- "불 커" → LIGHT_ON (받침 누락)
- "에어컨 커줘" → AC_ON (표준어 아님)
- "LED 커" → LED_ON

### 자연어 처리
- "좀 시원하게 해줘" → AC_ON (명확한 냉방 의도)
- "춥게 해" → AC_ON
- "가습기 좀 돌려" → HUM_ON

### 경계 케이스
- "등 켜" → LIGHT_ON (일반 조명)
- "상태등 켜" → LED_ON (상태등 우선)
- "불 다 꺼" → LIGHT_OFF (조명 끄기로 해석)

## 출력 형식
- 위 9가지 중 하나만 출력
- 대문자로 출력
- 언더스코어(_) 포함
- 설명, 이유, 기타 텍스트 일체 금지

## 분류 프로세스
1. 기기명 식별: 조명/에어컨/가습기/LED/없음
2. 동작 식별: 켜기/끄기/불명확
3. 조건 충족 확인
4. 애매하면 → UNKNOWN

## 현재 입력 분석
사용자 입력: "{user_command}"
→ 명령어:
    """
    
        try:
            response = self.model.generate_content(prompt)
            command = response.text.strip().upper()
            
            valid_commands = [
                "LIGHT_ON", "LIGHT_OFF", 
                "HUM_ON", "HUM_OFF",
                "AC_ON", "AC_OFF",
                "LED_ON", "LED_OFF",
                "UNKNOWN"
            ]
            
            if command in valid_commands:
                return command
            else:
                print(f"[GEMINI] 잘못된 응답: {command} → UNKNOWN 처리")
                return "UNKNOWN"
                
        except Exception as e:
            print(f"❌ Gemini 오류: {e}")
            return "UNKNOWN"