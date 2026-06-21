# Azure AI Speech 실습

이 폴더는 Azure AI Speech 서비스를 사용해 음성 인식, 음성 합성, 음성 번역, 발음 평가 기능을 실습한 내용을 정리한 공간입니다.

이번 실습에서는 Azure Speech SDK와 Gradio를 사용하여 음성 AI 기능을 직접 웹 화면에 연결했습니다.

## 실습 목표

Azure AI Speech의 주요 기능을 Python 코드로 호출하고, Gradio를 이용해 사용자가 직접 테스트할 수 있는 간단한 웹 앱을 만드는 것이 목표입니다.

이 폴더에서는 다음 기능을 다룹니다.

| 번호 | 실습 폴더 | 기능 |
|---|---|---|
| 01 | `01-speech-to-text` | 음성을 텍스트로 변환 |
| 02 | `02-text-to-speech` | 텍스트를 음성으로 변환 |
| 03 | `03-speech-translation` | 한국어 음성을 영어와 일본어로 번역 |
| 04 | `04-pronunciation-assessment` | 영어 발음 평가 |
| 05 | `05-integrated-speech-app` | 위 네 가지 기능을 하나의 Gradio 앱으로 통합 |

## 전체 실습 흐름

```text
Azure Speech 리소스 생성
→ Endpoint와 Key 확인
→ .env 파일에 환경 변수 저장
→ Azure Speech SDK로 기능 호출
→ Gradio 화면에서 입력 받기
→ 결과를 텍스트, 오디오, 표 형태로 출력
```

## 폴더 구조

```text
04-ai-speech/
├── README.md
├── 01-speech-to-text/
│   ├── app.py
│   └── README.md
├── 02-text-to-speech/
│   ├── app.py
│   └── README.md
├── 03-speech-translation/
│   ├── app.py
│   └── README.md
├── 04-pronunciation-assessment/
│   ├── app.py
│   └── README.md
├── 05-integrated-speech-app/
│   ├── app.py
│   ├── speech_service.py
│   ├── README.md
│   └── outputs/
├── notebooks/
│   └── ai_speech_practice.ipynb
├── sample-data/
│   └── sample.wav
└── outputs/
```

## 사용 기술

| 기술 | 역할 |
|---|---|
| Azure AI Speech | 음성 인식, 음성 합성, 음성 번역, 발음 평가 기능 제공 |
| Azure Speech SDK | Python 코드에서 Azure Speech 기능 호출 |
| Gradio | 음성 입력, 텍스트 출력, 오디오 출력 화면 구성 |
| python-dotenv | `.env` 파일에서 환경 변수 로드 |
| pandas | 발음 평가 결과를 표 형태로 정리 |

## 환경 변수 설정

프로젝트 루트 또는 해당 실습 폴더에 `.env` 파일을 생성하고 아래 값을 입력합니다.

```env
AZURE_SPEECH_ENDPOINT=your_azure_speech_endpoint
AZURE_SPEECH_KEY=your_azure_speech_key
```

`.env` 파일은 실제 Key가 들어가기 때문에 GitHub에 업로드하면 안 됩니다.

`.env.example` 파일만 공유하고, 실제 `.env` 파일은 `.gitignore`에 추가합니다.

## 설치 방법

루트 폴더에서 필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

또는 Speech 실습용으로만 설치하려면 아래 패키지가 필요합니다.

```bash
pip install gradio azure-cognitiveservices-speech python-dotenv pandas
```

## 실행 방법

각 기능별 폴더로 이동한 뒤 `app.py`를 실행합니다.

예시:

```bash
cd 04-ai-speech/01-speech-to-text
python app.py
```

통합 앱을 실행하려면 아래처럼 실행합니다.

```bash
cd 04-ai-speech/05-integrated-speech-app
python app.py
```

실행 후 브라우저에 표시되는 Gradio URL로 접속하면 앱을 사용할 수 있습니다.

## 실습별 설명

### 1. Speech to Text

마이크로 입력한 한국어 음성을 텍스트로 변환합니다.

```text
마이크 입력
→ Azure Speech SDK
→ 한국어 텍스트 출력
```

### 2. Text to Speech

사용자가 입력한 텍스트를 한국어 음성 파일로 변환합니다.

```text
텍스트 입력
→ Azure Speech SDK
→ output.wav 생성
→ Gradio 오디오 플레이어 출력
```

### 3. Speech Translation

한국어 음성을 입력받아 영어와 일본어 텍스트로 번역합니다.

```text
한국어 음성 입력
→ 음성 인식
→ 영어 번역
→ 일본어 번역
```

### 4. Pronunciation Assessment

사용자가 영어 문장을 읽으면 기준 문장과 비교해 발음 점수를 계산합니다.

```text
기준 영어 문장 입력
→ 사용자 음성 입력
→ 발음 평가
→ 종합 점수, 정확도, 유창성, 완성도 출력
```

### 5. Integrated Speech App

앞에서 만든 네 가지 기능을 하나의 Gradio 앱으로 합친 실습입니다.

```text
STT 탭
TTS 탭
Speech Translation 탭
Pronunciation Assessment 탭
```

## 주의사항

- Azure Speech Key는 코드에 직접 작성하지 않습니다.
- `.env` 파일은 GitHub에 업로드하지 않습니다.
- 마이크 입력이 안 될 경우 브라우저의 마이크 권한을 확인합니다.
- 음성 인식 언어와 실제 말하는 언어가 다르면 결과가 부정확할 수 있습니다.
- 발음 평가는 기준 문장 언어와 `speech_recognition_language` 설정이 맞아야 합니다.

## 다음 확장 아이디어

이 실습을 바탕으로 다음과 같은 앱으로 확장할 수 있습니다.

- 음성 챗봇
- 실시간 통역 앱
- 영어 발음 학습 앱
- 회의록 자동 생성 앱
- STT 결과를 Azure AI Language로 분석하는 앱