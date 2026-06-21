# 05-ai-vision/05-object-detection/analyze_objects.py

import sys
from pathlib import Path

from azure.ai.vision.imageanalysis.models import VisualFeatures

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common_vision import (
    bounding_box_to_dict,
    create_vision_client,
    load_image_bytes,
    save_json,
)


def analyze_objects(image_name: str = "sample.jpg") -> dict:
    """
    이미지 속 객체와 사람 위치를 추출한다.
    Objects는 일반 객체를 찾고,
    People은 이미지 속 사람 위치를 찾는다.
    """
    client = create_vision_client()
    image_data = load_image_bytes(image_name)

    result = client.analyze(
        image_data=image_data,
        visual_features=[
            VisualFeatures.OBJECTS,
            VisualFeatures.PEOPLE,
        ],
    )

    output = {
        "image_name": image_name,
        "objects": [],
        "people": [],
    }

    if result.objects is not None:
        for detected_object in result.objects.list:
            best_tag = detected_object.tags[0] if detected_object.tags else None

            output["objects"].append(
                {
                    "name": best_tag.name if best_tag else None,
                    "confidence": best_tag.confidence if best_tag else None,
                    "bounding_box": bounding_box_to_dict(detected_object.bounding_box),
                }
            )

    if result.people is not None:
        for person in result.people.list:
            output["people"].append(
                {
                    "confidence": person.confidence,
                    "bounding_box": bounding_box_to_dict(person.bounding_box),
                }
            )

    return output


def main() -> None:
    result = analyze_objects("sample.jpg")
    save_json(result, "object_detection_results.json")
    print(result)


if __name__ == "__main__":
    main()