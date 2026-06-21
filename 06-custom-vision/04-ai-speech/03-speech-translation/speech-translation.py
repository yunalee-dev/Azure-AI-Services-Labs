import gradio as gr
import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")
KEY = os.getenv("AZURE_SPEECH_KEY")

def request_translation_sdk(audio_path):
    if audio_path is None:
        return "오디오 파일이 없습니다.", ""
    
    try:
        # 1. 🌟 SpeechTranslationConfig 설정 (일반 SpeechConfig가 아닙니다!)
        translation_config = speechsdk.translation.SpeechTranslationConfig(
            subscription=KEY, 
            endpoint=ENDPOINT
        )
        
        # 2. 언어 설정
        translation_config.speech_recognition_language = "ko-KR"  # 말하는 사람의 언어
        translation_config.add_target_language("en")             # 번역 목표 언어 1: 영어
        translation_config.add_target_language("ja")             # 번역 목표 언어 2: 일본어
        
        # 3. 오디오 입력 설정
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        
        # 4. 🌟 번역 인식기(TranslationRecognizer) 생성
        translation_recognizer = speechsdk.translation.TranslationRecognizer(
            translation_config=translation_config, 
            audio_config=audio_config
        )
        
        print(f"▶ [SDK 번역 테스트] 오디오 처리 중: {audio_path}")
        
        # 5. 음성 번역 실행 (단발성)
        result = translation_recognizer.recognize_once()
        
        # 6. 결과 분석 및 반환
        if result.reason == speechsdk.ResultReason.TranslatedSpeech:
            print(" 성공: 음성 번역 완료")
            print(f"원문(KO): {result.text}")
            
            # 번역된 결과들은 result.translations 딕셔너리에 담겨 옵니다.
            english_text = result.translations.get("en", "번역 실패")
            japanese_text = result.translations.get("ja", "번역 실패")
            
            return english_text, japanese_text
            
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "음성을 인식하지 못했습니다.", "음성을 인식하지 못했습니다."
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                return f"에러: {cancellation_details.error_details}", ""
            return "번역이 취소되었습니다.", ""
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return f"실행 에러: {e}", ""

# Gradio 화면 구성
with gr.Blocks() as demo:
    gr.Markdown("# Yuna's AI World!!!! (Translation SDK Version)")
    
    with gr.Column():
        gr.Markdown('### Speech Translation (한국어 🗣️ ➔ 영어🇺🇸/일본어🇯🇵 번역)')
        
        # 마이크 입력
        input_mic = gr.Audio(
            label="마이크 입력 (한국어로 말씀하세요)", 
            sources="microphone", 
            type="filepath"
        )
        
        # 번역 결과를 보여줄 2개의 텍스트 상자
        output_en = gr.Textbox(label="영어 번역 결과 (English)", interactive=False)
        output_ja = gr.Textbox(label="일본어 번역 결과 (日本語)", interactive=False)
        
        # 마이크 입력이 끝나면 자동으로 번역 함수 호출 및 결과 반영
        input_mic.change(
            fn=request_translation_sdk, 
            inputs=[input_mic], 
            outputs=[output_en, output_ja]
        )

demo.launch(share=True)