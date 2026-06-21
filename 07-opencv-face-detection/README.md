# OpenCV Face Detection 실습

OpenCV와 Haar Cascade를 사용해 이미지와 웹캠에서 얼굴을 감지하는 실습입니다.

## 실습 목표

- OpenCV로 이미지 읽기
- Haar Cascade 분류기 로딩
- 이미지에서 얼굴 감지
- Bounding Box 그리기
- Gradio로 얼굴 감지 결과 확인
- 웹캠으로 실시간 얼굴 감지

## 폴더 구조

```text
07-opencv-face-detection/
│
├── README.md
├── requirements.txt
├── app.py
├── face_detection.py
│
├── notebooks/
│   └── 01-opencv-face-detection.ipynb
│
├── sample-data/
│   ├── README.md
│   └── sample_face.jpg
│
└── outputs/
    └── .gitkeep