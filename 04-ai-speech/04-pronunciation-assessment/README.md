# Pronunciation Assessment 실습

이 폴더는 Azure Speech SDK를 사용해 사용자의 영어 발음을 평가하는 실습 코드입니다.

Pronunciation Assessment는 사용자가 읽은 음성을 기준 문장과 비교하여 발음 점수를 계산하는 기능입니다.

## 실습 목표

사용자가 기준 영어 문장을 읽으면 Azure Speech SDK가 음성을 인식하고, 발음 점수를 계산하여 Gradio 화면에 표 형태로 출력합니다.

## 실행 흐름

```text
기준 영어 문장 입력
→ 사용자가 마이크로 문장 읽기
→ Azure Speech SDK로 음성 인식
→ 기준 문장과 비교
→ 발음 점수 계산
→ Gradio에 결과 출력
```

## 주요 파일

```text
04-pronunciation-assessment/
├── app.py
└── README.md
```

## 사용 기술

| 기술 | 역할 |
|---|---|
| Gradio | 기준 문장 입력, 마이크 입력, 점수 출력 |
| Azure Speech SDK | 음성 인식과 발음 평가 |
| pandas | 발음 평가 점수를 표로 정리 |
| python-dotenv | Azure Endpoint와 Key를 환경 변수로 로드 |

## 환경 변수

`.env` 파일에 아래 값을 설정합니다.

```env
AZURE_SPEECH_ENDPOINT=your_azure_speech_endpoint
AZURE_SPEECH_KEY=your_azure_speech_key
```

## 핵심 코드 설명

```python
speech_config = speechsdk.SpeechConfig(
    subscription=KEY,
    endpoint=ENDPOINT
)
```

Azure Speech 서비스에 연결합니다.

```python
speech_config.speech_recognition_language = "en-US"
```

이번 실습은 영어 발음 평가이므로 인식 언어를 `en-US`로 설정합니다.

```python
pronunciation_config = speechsdk.PronunciationAssessmentConfig(
    reference_text=reference_text,
    grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
    granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme
)
```

발음 평가 설정을 만듭니다.

| 설정 | 의미 |
|---|---|
| `reference_text` | 사용자가 따라 읽을 기준 문장 |
| `HundredMark` | 100점 만점 방식으로 평가 |
| `Phoneme` | 음소 단위로 세밀하게 평가 |

```python
pronunciation_config.apply_to(speech_recognizer)
```

발음 평가 설정을 음성 인식기에 적용합니다.

```python
assessment_result = speechsdk.PronunciationAssessmentResult(result)
```

음성 인식 결과에서 발음 평가 점수를 추출합니다.

## 평가 항목

| 평가 항목 | 의미 |
|---|---|
| Pronunciation Score | 전체 발음 종합 점수 |
| Accuracy Score | 기준 발음과 얼마나 정확히 일치하는지 |
| Fluency Score | 얼마나 자연스럽고 끊김 없이 말했는지 |
| Completeness Score | 기준 문장을 얼마나 빠짐없이 읽었는지 |

## Gradio 화면 구성

```python
ref_textbox = gr.Textbox(
    label="따라 읽을 문장",
    value="Today is a beautiful day to practice computer programming."
)

input_mic = gr.Audio(
    label="위 문장을 마이크로 읽어주세요",
    sources="microphone",
    type="filepath"
)

submit_btn = gr.Button("발음 평가하기")

output_text = gr.Textbox(
    label="결과 요약",
    interactive=False
)

output_table = gr.Dataframe(
    label="상세 발음 점수"
)
```

기준 문장, 마이크 입력, 평가 버튼, 결과 요약, 점수 표로 구성됩니다.

## 실행 방법

```bash
cd 04-ai-speech/04-pronunciation-assessment
python app.py
```

## 결과 예시

```text
기준 문장:
Today is a beautiful day to practice computer programming.

결과 요약:
인식된 텍스트: "Today is a beautiful day to practice computer programming."

점수:
종합 점수: 87
정확도: 85
유창성: 90
완성도: 92
```

## 자주 발생하는 오류

| 오류 상황 | 원인 | 해결 방법 |
|---|---|---|
| 발음 평가가 안 됨 | 기준 문장이 비어 있음 | 기준 문장 입력 |
| 음성을 인식하지 못함 | 마이크 입력 문제 | 마이크 권한과 볼륨 확인 |
| 점수가 이상함 | 기준 문장과 다르게 읽음 | 문장을 정확히 읽기 |
| 영어가 아닌 언어로 읽음 | 언어 설정 불일치 | `en-US` 기준으로 영어 문장 사용 |

## 정리

이 실습에서는 Azure Speech SDK의 발음 평가 기능을 사용했습니다.

발음 평가는 영어 학습 앱, 말하기 연습 서비스, AI 튜터 앱으로 확장하기 좋은 기능입니다.