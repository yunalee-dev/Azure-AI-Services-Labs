# make_detection_regions.py

import json
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DETECTION_DIR = BASE_DIR / "sample-data" / "detection"
LABEL_DIR = BASE_DIR / "sample-data" / "labels"
OUTPUT_PATH = LABEL_DIR / "detection_regions.json"

LABEL_DIR.mkdir(parents=True, exist_ok=True)

label_data = {
    "fork": {},
    "scissors": {}
}

target_folders = {
    "fork": DETECTION_DIR / "fork",
    "scissors": DETECTION_DIR / "scissors"
}

for tag_name, folder_path in target_folders.items():
    if not folder_path.exists():
        print(f"폴더가 없습니다: {folder_path}")
        continue

    image_paths = sorted([
        path for path in folder_path.iterdir()
        if path.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ])

    print(f"\n[{tag_name}] 이미지 {len(image_paths)}개 처리 시작")

    for image_path in image_paths:
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"이미지를 읽을 수 없습니다: {image_path}")
            continue

        height, width = image.shape[:2]

        print(f"\n이미지: {image_path.name}")
        print("마우스로 객체 영역을 드래그한 뒤 Enter 또는 Space를 누르세요.")
        print("건너뛰려면 c를 누르세요.")

        x, y, w, h = cv2.selectROI(
            f"Select box - {tag_name} - {image_path.name}",
            image,
            fromCenter=False,
            showCrosshair=True
        )

        cv2.destroyAllWindows()

        if w == 0 or h == 0:
            print(f"건너뜀: {image_path.name}")
            continue

        left = x / width
        top = y / height
        box_width = w / width
        box_height = h / height

        box = [
            round(left, 6),
            round(top, 6),
            round(box_width, 6),
            round(box_height, 6)
        ]

        label_data[tag_name][image_path.name] = box

        print("저장된 좌표:", box)

with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
    json.dump(label_data, file, ensure_ascii=False, indent=2)

print("\nJSON 저장 완료")
print(OUTPUT_PATH)