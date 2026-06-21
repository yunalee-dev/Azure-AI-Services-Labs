# 05-ai-vision/04-common-tag-extraction/analyze_tags.py

import sys
from pathlib import Path

from azure.ai.vision.imageanalysis.models import VisualFeatures

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common_vision import create_vision_client, load_image_bytes, save_json


def analyze_tags(image_name: str = "sample.jpg") -> dict:
    """
    이미지 전체를 설명하는 공통 태그를 추출한다.
    예: indoor, person, table, laptop, food, building 등
    """
    client = create_vision_client()
    image_data = load_image_bytes(image_name)

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.TAGS],
    )

    output = {
        "image_name": image_name,
        "tags": [],
    }

    if result.tags is not None:
        for tag in result.tags.list:
            output["tags"].append(
                {
                    "name": tag.name,
                    "confidence": tag.confidence,
                }
            )

    return output


def main() -> None:
    result = analyze_tags("sample.jpg")
    save_json(result, "tag_results.json")
    print(result)


if __name__ == "__main__":
    main()