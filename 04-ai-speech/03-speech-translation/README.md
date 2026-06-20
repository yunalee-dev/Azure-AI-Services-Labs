# Text to Speech 실습

이 폴더는 Azure Speech SDK를 사용해 텍스트를 음성으로 변환하는 TTS 실습 코드입니다.

TTS는 Text to Speech의 약자로, 사용자가 입력한 텍스트를 사람이 말하는 것 같은 음성 파일로 변환하는 기능입니다.

## 실습 목표

사용자가 Gradio 화면에 텍스트를 입력하면 Azure Speech SDK가 해당 문장을 음성으로 합성하고, 생성된 음성 파일을 Gradio 오디오 컴포넌트에서 재생합니다.

## 실행 흐름

```text
텍스트 입력
→ Azure Speech SDK SpeechSynthesizer 실행
→ 한국어 음성 합성
→ output.wav 파일 생성
→ Gradio 오디오 플레이어에서 재생
```

## 주요 파일

```text
02-text-to-speech/
├── app.py
└── README.md
```

## 사용 기술

| 기술 | 역할 |
|---|---|
| Gradio | 텍스트 입력과 오디오 출력 화면 구성 |
| Azure Speech SDK | 텍스트를 음성으로 변환 |
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

Azure Speech 서비스에 연결하기 위한 설정입니다.

```python
speech_config.speech_synthesis_voice_name = "ko-KR-SunHiNeural"
```

음성 합성에 사용할 목소리를 설정합니다.

이번 실습에서는 한국어 여성 음성인 `ko-KR-SunHiNeural`을 사용했습니다.

다른 목소리를 사용하고 싶다면 아래와 같이 변경할 수 있습니다.

```python
speech_config.speech_synthesis_voice_name = "ko-KR-InJoonNeural"
```

```python
audio_config = speechsdk.audio.AudioConfig(filename=output_path)
```

생성된 음성을 저장할 파일 경로를 설정합니다.

```python
speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)
```

`SpeechSynthesizer`는 텍스트를 음성으로 변환하는 객체입니다.

```python
result = speech_synthesizer.speak_text_async(text).get()
```

입력된 텍스트를 음성으로 합성합니다.

## Gradio 화면 구성

```python
input_textbox = gr.Textbox(
    label="텍스트 입력",
    placeholder="음성으로 바꿀 내용을 입력하세요."
)

submit_button = gr.Button("음성으로 변환하기")

output_audio = gr.Audio(
    label="변환된 음성 결과",
    type="filepath"
)
```

사용자는 텍스트를 입력하고 버튼을 누릅니다.

함수는 생성된 `output.wav` 파일 경로를 반환하고, Gradio는 해당 파일을 오디오 플레이어에 표시합니다.

## 실행 방법

```bash
cd 04-ai-speech/02-text-to-speech
python app.py
```

## 결과 예시

```text
입력: 안녕하세요. Azure Speech SDK로 만든 음성입니다.
출력: output.wav 음성 파일 생성
```

## 자주 발생하는 오류

| 오류 상황 | 원인 | 해결 방법 |
|---|---|---|
| 음성 파일이 생성되지 않음 | Key 또는 Endpoint 오류 | `.env` 값 확인 |
| 소리가 재생되지 않음 | 파일 경로 문제 | `output.wav` 생성 여부 확인 |
| 목소리가 원하는 언어가 아님 | voice name 설정 오류 | `speech_synthesis_voice_name` 확인 |
| 버튼을 눌러도 반응 없음 | 입력 텍스트가 비어 있음 | 텍스트 입력 후 실행 |

## 정리

이 실습에서는 텍스트를 음성으로 변환하는 TTS 기능을 구현했습니다.

TTS는 챗봇 답변을 음성으로 들려주거나, 안내 방송, AI 튜터, 내레이션 생성 서비스에 활용할 수 있습니다.