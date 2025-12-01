import speech_recognition as sr
import google.generativeai as genai
import os
from typing import Optional

# Gemini API 설정
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # 실제 API 키로 교체 필요
genai.configure(api_key=GEMINI_API_KEY)

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.model = genai.GenerativeModel('gemini-pro')
        
        # 마이크 노이즈 조정
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def listen_for_trigger(self) -> bool:
        """
        "두노야" 트리거 감지
        """
        try:
            with self.microphone as source:
                print("[VOICE] 트리거 대기중... ('두노야'를 말해주세요)")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
            text = self.recognizer.recognize_google(audio, language='ko-KR')
            print(f"[VOICE] 감지된 음성: {text}")
            
            if "두노야" in text or "두노" in text:
                print("[VOICE] 트리거 감지! 명령을 말해주세요.")
                return True
                
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"[VOICE ERROR] {e}")
            
        return False
    
    def listen_for_command(self) -> Optional[str]:
        """
        트리거 후 실제 명령 인식
        """
        try:
            with self.microphone as source:
                print("[VOICE] 명령 대기중...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
            text = self.recognizer.recognize_google(audio, language='ko-KR')
            print(f"[VOICE] 인식된 명령: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("[VOICE] 타임아웃")
        except sr.UnknownValueError:
            print("[VOICE] 음성을 인식할 수 없습니다")
        except Exception as e:
            print(f"[VOICE ERROR] {e}")
            
        return None
    
    def interpret_with_gemini(self, user_command: str) -> str:
        """
        Gemini API로 자연어 명령 해석
        """
        prompt = f"""
        사용자가 스마트홈 제어 명령을 말했습니다: "{user_command}"
        
        다음 중 어떤 명령인지 정확히 하나만 응답해주세요:
        - LIGHT_ON: 조명 켜기
        - LIGHT_OFF: 조명 끄기  
        - HUM_ON: 가습기 켜기
        - HUM_OFF: 가습기 끄기
        - AC_ON: 에어컨 켜기
        - AC_OFF: 에어컨 끄기
        - LED_ON: 상태등 켜기
        - LED_OFF: 상태등 끄기
        - UNKNOWN: 위 명령이 아님
        
        응답은 반드시 위 명령어 중 하나만 정확히 출력하세요.
        """
        
        try:
            response = self.model.generate_content(prompt)
            command = response.text.strip()
            print(f"[GEMINI] 해석된 명령: {command}")
            return command
        except Exception as e:
            print(f"[GEMINI ERROR] {e}")
            return "UNKNOWN"

def recognize_voice() -> Optional[str]:
    """
    메인 음성 인식 함수
    """
    voice = VoiceRecognizer()
    
    # 1. 트리거 감지
    if voice.listen_for_trigger():
        # 2. 명령 인식
        user_command = voice.listen_for_command()
        if user_command:
            # 3. Gemini로 해석
            return voice.interpret_with_gemini(user_command)
    
    return None