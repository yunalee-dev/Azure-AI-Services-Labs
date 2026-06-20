import gradio as gr
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")
KEY = os.getenv("AZURE_SPEECH_KEY")

def request_stt_sdk(audio_path):
    if audio_path is None:
        return ""
    
    try:
        # 1. Azure Speech SDK 설정 (Key와 Endpoint 주소 활용)
        speech_config = speechsdk.SpeechConfig(subscription=KEY, endpoint=ENDPOINT)
        
        # 한국어 음성 인식을 위해 언어 설정 추가 (필수!)
        speech_config.speech_recognition_language = "ko-KR"
        
        # 2. 오디오 파일 입력 설정
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        
        # 3. 인식기 생성
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        print(f"▶ [SDK 테스트] 오디오 파일 처리 중: {audio_path}")
        
        # 4. 음성 인식 실행 (단발성 인식)
        result = speech_recognizer.recognize_once()
        
        # 5. 결과 분석 및 반환
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f" 성공: {result.text}")
            return result.text
            
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("❌ 인식 실패: 음성을 감지하지 못했거나 매칭되는 단어가 없음")
            return "음성을 인식하지 못했습니다. (소리가 너무 작거나 유효한 오디오가 아님)"
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ 취소됨: {cancellation_details.reason}")
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"❌ 에러 상세 정보: {cancellation_details.error_details}")
                # 엔드포인트나 키 주소가 잘못되었을 때 상세 메시지를 반환해 줍니다.
                return f"Azure SDK 에러: {cancellation_details.error_details}"
                
            return "음성 인식이 취소되었습니다."
            
    except Exception as e:
        print(f"❌ 코드 실행 중 예외 발생: {e}")
        return f"실행 에러: {e}"

def change_audio(audio_path):
    text = request_stt_sdk(audio_path)
    return text

# Gradio 화면 구성
with gr.Blocks() as demo:
    gr.Markdown("# Yuna's AI World!!!! (SDK Version)")
    
    with gr.Column(scale=1):
        gr.Markdown('### STT (Azure Speech SDK)')
        input_mic = gr.Audio(
            label="마이크 입력", 
            sources="microphone", 
            type="filepath"
        )
        output_textbox = gr.Textbox(label="텍스트", placeholder="변환된 텍스트", interactive=False)
        
        # 이벤트 연결
        input_mic.change(fn=change_audio, inputs=[input_mic], outputs=[output_textbox])

demo.launch(share=True)