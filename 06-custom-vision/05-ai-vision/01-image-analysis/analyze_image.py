# 05-ai-vision/01-image-analysis/analyze_image.py

import sys
from pathlib import Path

from azure.ai.vision.imageanalysis.models import VisualFeatures

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common_vision import (
    bounding_box_to_dict,
    create_vision_client,
    load_image_bytes,
    polygon_to_list,
    save_json,
)


def analyze_image(image_name: str = "sample.jpg") -> dict:
    """
    하나의 이미지에서 캡션, 태그, 객체 감지, OCR 결과를 함께 추출한다.
    """
    client = create_vision_client()
    image_data = load_image_bytes(image_name)

    result = client.analyze(
        image_data=image_data,
        visual_features=[
            VisualFeatures.CAPTION,
            VisualFeatures.TAGS,
            VisualFeatures.OBJECTS,
            VisualFeatures.READ,
        ],
        gender_neutral_caption=True,
    )

    output = {
        "image_name": image_name,
        "caption": None,
        "tags": [],
        "objects": [],
        "read": [],
    }

    if result.caption is not None:
        output["caption"] = {
            "text": result.caption.text,
            "confidence": result.caption.confidence,
        }

    if result.tags is not None:
        for tag in result.tags.list:
            output["tags"].append(
                {
                    "name": tag.name,
                    "confidence": tag.confidence,
                }
            )

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

    if result.read is not None and result.read.blocks:
        for block in result.read.blocks:
            for line in block.lines:
                output["read"].append(
                    {
                        "text": line.text,
                        "bounding_polygon": polygon_to_list(line.bounding_polygon),
                        "words": [
                            {
                                "text": word.text,
                                "confidence": word.confidence,
                                "bounding_polygon": polygon_to_list(word.bounding_polygon),
                            }
                            for word in line.words
                        ],
                    }
                )

    return output


def main() -> None:
    result = analyze_image("sample.jpg")
    save_json(result, "image_analysis_results.json")
    print(result)


if __name__ == "__main__":
    main()