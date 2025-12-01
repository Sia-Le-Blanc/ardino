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
        frequencies = [523, 659, 784]  # 도(C), 미(E), 솔(G)
        
        for freq in frequencies:
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            wave = np.sin(2 * np.pi * freq * t) * 0.3
            sd.play(wave, self.sample_rate)
            sd.wait()
    
    def listen_continuous(self) -> bool:
        """24시간 대기 모드"""
        try:
            print("[VOICE] 트리거 대기중...")
            audio = self.record_audio(duration=3)
            text = self.audio_to_text(audio)
            
            # "준호" 트리거 (오인식 포함)
            if any(word in text for word in ["준호", "주노", "존호", "전호"]):
                print(f"[VOICE] 트리거 감지: {text}")
                self.play_beep()
                return True
        except:
            pass
        return False
    
    def listen_for_command(self) -> Optional[str]:
        """명령 대기 모드"""
        try:
            print("[VOICE] 명령을 말씀해주세요...")
            audio = self.record_audio(duration=5)
            text = self.audio_to_text(audio)
            print(f"[VOICE] 인식된 명령: {text}")
            return text
        except Exception as e:
            print(f"[VOICE ERROR] {e}")
            return None
    
    def interpret_with_gemini(self, user_command: str) -> str:
        """Gemini로 명령 정교하게 해석"""
        prompt = f"""
당신은 스마트홈 음성 비서의 명령 분류 AI입니다.
사용자의 음성을 정확히 분석하여 **오직 하나의 명령어만** 반환하세요.

[사용자 입력]
"{user_command}"

[가능한 명령어 및 조건]
1. LIGHT_ON
   - 조건: "조명", "불", "라이트", "등", "전등"을 켜달라는 명령
   - 예시: "불 켜줘", "조명 켜", "라이트 온", "불 좀"
   
2. LIGHT_OFF
   - 조건: "조명", "불", "라이트", "등", "전등"을 끄달라는 명령
   - 예시: "불 꺼줘", "조명 꺼", "라이트 오프", "어둡게"

3. HUM_ON
   - 조건: "가습기"를 켜달라는 명령 (다른 기기 아님)
   - 예시: "가습기 켜줘", "가습기 틀어줘", "습도 올려"

4. HUM_OFF
   - 조건: "가습기"를 끄달라는 명령
   - 예시: "가습기 꺼줘", "가습기 끄기"

5. AC_ON
   - 조건: "에어컨", "냉방", "시원하게"를 켜달라는 명령
   - 예시: "에어컨 켜", "시원하게 해줘", "냉방 켜"

6. AC_OFF
   - 조건: "에어컨", "냉방"을 끄달라는 명령
   - 예시: "에어컨 꺼", "냉방 끄기"

7. LED_ON
   - 조건: "상태등", "LED", "엘이디", "표시등"을 켜달라는 명령
   - 예시: "상태등 켜", "LED 켜줘"

8. LED_OFF
   - 조건: "상태등", "LED", "엘이디", "표시등"을 끄달라는 명령
   - 예시: "상태등 꺼", "LED 끄기"

9. UNKNOWN
   - 위 8가지 중 어느 것도 해당하지 않는 경우
   - 예시: 질문, 인사, 잡담, 모호한 명령, 지원하지 않는 기기

[엄격한 분류 규칙]
✅ 반드시 지켜야 할 것:
- 명확한 "기기명 + 동작(켜기/끄기)"이 있어야 함
- 기기명이 정확히 일치해야 함 (가습기 ≠ 에어컨)
- 동작이 명확해야 함 (켜기/끄기/틀기/끄기 등)

❌ UNKNOWN으로 처리해야 하는 경우:
- "뭐 켜줘" (기기명 없음)
- "온도 낮춰줘" (동작이 모호함)
- "안녕", "고마워" (인사/감사)
- "몇 시야?", "날씨 어때?" (질문)
- "TV 켜줘", "커튼 열어줘" (지원하지 않는 기기)
- "잘 자" (명령 아님)

[출력 형식]
- 반드시 위 9가지 중 **정확히 하나만** 출력
- 설명 없이 명령어만 출력
- 대문자로 출력
- 예: LIGHT_ON

[분석 시작]
사용자 입력 "{user_command}"는 어떤 명령입니까?
        """
        
        try:
            response = self.model.generate_content(prompt)
            command = response.text.strip().upper()
            
            # 유효한 명령어인지 검증
            valid_commands = [
                "LIGHT_ON", "LIGHT_OFF", 
                "HUM_ON", "HUM_OFF",
                "AC_ON", "AC_OFF",
                "LED_ON", "LED_OFF",
                "UNKNOWN"
            ]
            
            if command in valid_commands:
                print(f"[GEMINI] 해석 결과: {command}")
                return command
            else:
                print(f"[GEMINI] 잘못된 응답: {command} → UNKNOWN 처리")
                return "UNKNOWN"
                
        except Exception as e:
            print(f"[GEMINI ERROR] {e}")
            return "UNKNOWN"

def recognize_voice() -> Optional[str]:
    """메인 음성 인식 루프"""
    voice = VoiceRecognizer()
    
    if voice.listen_continuous():
        user_command = voice.listen_for_command()
        if user_command:
            return voice.interpret_with_gemini(user_command)
    
    return None