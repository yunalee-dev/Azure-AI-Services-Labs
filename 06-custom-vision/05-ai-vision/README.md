# 05-ai-vision

Azure AI Vision을 사용해 이미지 분석, OCR, 이미지 캡션, 공통 태그 추출, 객체 감지를 실습하는 폴더입니다.

## 실습 목표

이미지 파일을 Azure AI Vision API로 분석하고, 결과를 JSON 파일로 저장합니다.

실습 기능은 다음과 같습니다.

- Image Analysis
- OCR
- Image Captioning
- Common Tag Extraction
- Object Detection

## 폴더 구조

```text
05-ai-vision/
├── README.md
├── common_vision.py
├── 01-image-analysis/
│   └── analyze_image.py
├── 02-ocr/
│   └── analyze_ocr.py
├── 03-image-captioning/
│   └── analyze_caption.py
├── 04-common-tag-extraction/
│   └── analyze_tags.py
├── 05-object-detection/
│   └── analyze_objects.py
├── notebooks/
├── sample-data/
│   └── sample.jpg
└── outputs/