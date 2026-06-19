# 02-rest-api

Azure AI Document Intelligence REST API를 사용하여 문서를 분석하는 실습입니다.

## 구성

```
02-rest-api
├── .env
├── .env.example
├── common.py
├── analyze_read.py
├── analyze_layout.py
├── analyze_invoice.py
└── README.md
```

## 파일 설명

| 파일 | 설명 |
|--------|------|
| common.py | REST API 호출, 결과 조회, JSON 저장 등 공통 함수 |
| analyze_read.py | OCR(Text Extraction) 수행 |
| analyze_layout.py | 문서 구조 및 표(Table) 추출 |
| analyze_invoice.py | Invoice 정보 추출 |
| .env | Endpoint, Key 저장 |
| .env.example | 환경 변수 예시 |

---

## 환경 변수 설정

`.env`

```env
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key
```

---

## 필요한 패키지

```bash
pip install requests python-dotenv
```

---

## 샘플 데이터

```
01-document-intelligence
├── sample-data
│   ├── database_basic.pdf
│   └── receipt.jpg
```

---

## 실행

### Read (OCR)

```bash
python analyze_read.py
```

모델:

```python
prebuilt-read
```

기능

- 텍스트 추출
- OCR

---

### Layout

```bash
python analyze_layout.py
```

모델:

```python
prebuilt-layout
```

기능

- 페이지 분석
- 문단 추출
- 표(Table) 추출
- 행(Row), 열(Column) 구조 인식

---

### Invoice

```bash
python analyze_invoice.py
```

모델:

```python
prebuilt-invoice
```

기능

- Vendor Name
- Invoice ID
- Invoice Date
- Total Amount

---

## 출력

결과는 JSON 형태로 저장됩니다.

```
outputs/
├── read_result.json
├── layout_result.json
└── invoice_result.json
```

---

## 학습 내용

- REST API 호출
- requests 사용
- 비동기 분석 결과 조회
- JSON Parsing
- OCR
- Layout Analysis
- Invoice Extraction
- Azure AI Document Intelligence