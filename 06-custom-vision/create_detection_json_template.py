import json
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

for tag_name in ["fork", "scissors"]:
    folder = DETECTION_DIR / tag_name

    if not folder.exists():
        print(f"폴더 없음: {folder}")
        continue

    for image_path in sorted(folder.glob("*")):
        if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        # 일단 임시값. 나중에 직접 수정해야 함.
        label_data[tag_name][image_path.name] = [0.0, 0.0, 1.0, 1.0]

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(label_data, f, ensure_ascii=False, indent=2)

print(f"JSON 템플릿 생성 완료: {OUTPUT_PATH}")