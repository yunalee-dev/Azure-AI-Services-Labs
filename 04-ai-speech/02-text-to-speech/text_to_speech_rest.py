import gradio as gr
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")
KEY = os.getenv("AZURE_SPEECH_KEY")

def request_tts_sdk(text):
    if not text or text.strip() == "":
        return None
    
    # 생성될 음성 파일명 정의
    output_path = "output.wav"
    
    try:
        # 1. Azure Speech SDK 설정 (Key와 Endpoint 주소 활용)
        speech_config = speechsdk.SpeechConfig(subscription=KEY, endpoint=ENDPOINT)
        
        # 한국어 목소리 설정 (기본값: 여성 음성 SunHi)
        # 남성 음성을 원하시면 "ko-KR-InJoonNeural" 등으로 변경 가능합니다.
        speech_config.speech_synthesis_voice_name = "ko-KR-SunHiNeural"
        
        # 2. 오디오 파일 출력 설정 (결과물을 wav 파일로 저장)
        audio_config = speechsdk.audio.AudioConfig(filename=output_path)
        
        # 3. 음성 합성기(Synthesizer) 생성
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        print(f"▶ [SDK 테스트] 텍스트 변환 중: {text}")
        
        # 4. 음성 합성 실행
        result = speech_synthesizer.speak_text_async(text).get()
        
        # 5. 결과 분석 및 반환
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f" 성공: 음성 파일 생성 완료 ({output_path})")
            return output_path
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ 취소됨: {cancellation_details.reason}")
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"❌ 에러 상세 정보: {cancellation_details.error_details}")
            return None
            
    except Exception as e:
        print(f"❌ 코드 실행 중 예외 발생: {e}")
        return None

# Gradio 화면 구성
with gr.Blocks() as demo:
    gr.Markdown("# Yuna's AI World!!!! (TTS SDK Version)")
    
    with gr.Column(scale=1):
        gr.Markdown('### TTS (Azure Speech SDK)')
        
        # 텍스트 입력창과 음성 출력을 위한 컴포넌트 배치
        input_textbox = gr.Textbox(label="텍스트 입력", placeholder="음성으로 바꿀 내용을 입력하세요.")
        submit_button = gr.Button("음성으로 변환하기")
        output_audio = gr.Audio(label="변환된 음성 결과", type="filepath")
        
        # 버튼을 클릭했을 때 음성 합성 함수 실행
        submit_button.click(
            fn=request_tts_sdk, 
            inputs=[input_textbox], 
            outputs=[output_audio]
        )

demo.launch(share=True)