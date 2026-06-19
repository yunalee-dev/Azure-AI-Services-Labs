# 02-ai-language

Azure AI Language의 기본 텍스트 분석 기능을 실습하는 폴더입니다.

## 실습 기능

| 폴더 | 기능 | 설명 |
|---|---|---|
| 01-ner | Named Entity Recognition | 텍스트에서 사람, 장소, 조직, 날짜 같은 엔터티를 추출합니다. |
| 02-pii-detection | PII Detection | 이메일, 전화번호, 주소 등 개인정보를 탐지하고 마스킹합니다. |
| 03-sentiment-analysis | Sentiment Analysis | 문장의 감정이 긍정, 부정, 중립인지 분석합니다. |
| 04-key-phrase-extraction | Key Phrase Extraction | 문장에서 핵심 표현을 추출합니다. |
| 05-translation | Translation | Azure Translator REST API로 텍스트를 번역합니다. |

## 폴더 구조

```text
02-ai-language/
├── README.md
├── 01-ner/
│   └── analyze_ner.py
├── 02-pii-detection/
│   └── analyze_pii.py
├── 03-sentiment-analysis/
│   └── analyze_sentiment.py
├── 04-key-phrase-extraction/
│   └── analyze_key_phrases.py
├── 05-translation/
│   └── translate_text.py
├── notebooks/
│   └── README.md
├── sample-data/
│   └── language_samples.json
└── outputs/
    └── .gitkeep