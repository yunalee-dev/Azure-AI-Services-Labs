import gradio as gr
import azure.cognitiveservices.speech as speechsdk
import os
import pandas as pd
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")
KEY = os.getenv("AZURE_SPEECH_KEY")

def evaluate_pronunciation(audio_path, reference_text):
    if audio_path is None or not reference_text.strip():
        return "오디오 파일 또는 기준 텍스트가 없습니다.", None
    
    try:
        # 1. Azure Speech SDK 설정
        speech_config = speechsdk.SpeechConfig(subscription=KEY, endpoint=ENDPOINT)
        
        # 평가할 언어 설정 (예: 영어 발음 평가 'en-US' / 한국어 발음 평가는 'ko-KR')
        # 학습 목적에 맞게 수정 가능합니다. 여기서는 기본적으로 영어(en-US)로 설정했습니다.
        speech_config.speech_recognition_language = "en-US"
        
        # 2. 오디오 입력 설정
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        
        # 3. 발음 평가 설정 (정밀도 및 평가 모드 설정)
        # Phoneme(음소) 단위까지 세밀하게 평가하도록 설정 가능
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=reference_text,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark, # 100점 만점 시스템
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme # 음소 단위 세부 평가
        )
        
        # 4. 인식기 생성 및 발음 평가 설정 적용
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        pronunciation_config.apply_to(speech_recognizer)
        
        print(f"▶ [SDK 발음 평가] 오디오 처리 중...")
        
        # 5. 실행
        result = speech_recognizer.recognize_once()
        
        # 6. 결과 분석 및 반환
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # 발음 평가 결과 객체 추출
            assessment_result = speechsdk.PronunciationAssessmentResult(result)
            
            # 점수 데이터 구성 (종합 점수, 정확도, 유창성, 완벽도)
            scores = {
                "평가 항목": ["종합 점수 (Pronunciation Score)", "정확도 (Accuracy Score)", "유창성 (Fluency Score)", "완벽도 (Completeness Score)"],
                "점수 (100점 만점)": [
                    assessment_result.pronunciation_score,
                    assessment_result.accuracy_score,
                    assessment_result.fluency_score,
                    assessment_result.completeness_score
                ]
            }
            
            # Gradio에서 표 형태로 보여주기 위해 Pandas DataFrame으로 변환
            df_scores = pd.DataFrame(scores)
            
            summary_text = f"📢 인식된 텍스트: \"{result.text}\"\n🎉 평가가 완료되었습니다! 아래 표에서 점수를 확인하세요."
            return summary_text, df_scores
            
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "음성을 인식하지 못했습니다. 소리가 너무 작거나 유효한 오디오가 아닙니다.", None
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                return f"에러: {cancellation_details.error_details}", None
            return "발음 평가가 취소되었습니다.", None
            
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return f"실행 에러: {e}", None

# Gradio 화면 구성
with gr.Blocks() as demo:
    gr.Markdown("# Yuna's AI World!!!! (Pronunciation Assessment SDK Version)")
    
    with gr.Column():
        gr.Markdown('### Pronunciation Assessment (AI 영어 발음 평가 📝)')
        
        # 따라 읽을 기준 텍스트 입력창 (기본 예시 문장 제공)
        ref_textbox = gr.Textbox(
            label="따라 읽을 문장 (Reference Text)", 
            value="Today is a beautiful day to practice computer programming."
        )
        
        # 마이크 입력
        input_mic = gr.Audio(
            label="위 문장을 마이크로 읽어주세요 🗣️", 
            sources="microphone", 
            type="filepath"
        )
        
        # 버튼 생성
        submit_btn = gr.Button("발음 평가하기 🚀")
        
        # 결과 출력창 (텍스트 요약 & 점수 표)
        output_text = gr.Textbox(label="결과 요약", interactive=False)
        output_table = gr.Dataframe(label="상세 발음 점수")
        
        # 버튼 클릭 이벤트 연결
        submit_btn.click(
            fn=evaluate_pronunciation, 
            inputs=[input_mic, ref_textbox], 
            outputs=[output_text, output_table]
        )

demo.launch(share=True)