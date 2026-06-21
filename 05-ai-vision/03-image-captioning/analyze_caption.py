# 05-ai-vision/03-image-captioning/analyze_caption.py

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


def analyze_caption(image_name: str = "sample.jpg") -> dict:
    """
    이미지 전체 캡션과 Dense Captions를 추출한다.
    Caption은 이미지 전체를 설명하는 문장이고,
    Dense Captions는 이미지의 여러 영역을 설명하는 문장이다.
    """
    client = create_vision_client()
    image_data = load_image_bytes(image_name)

    result = client.analyze(
        image_data=image_data,
        visual_features=[
            VisualFeatures.CAPTION,
            VisualFeatures.DENSE_CAPTIONS,
        ],
        gender_neutral_caption=True,
    )

    output = {
        "image_name": image_name,
        "caption": None,
        "dense_captions": [],
    }

    if result.caption is not None:
        output["caption"] = {
            "text": result.caption.text,
            "confidence": result.caption.confidence,
        }

    if result.dense_captions is not None:
        for caption in result.dense_captions.list:
            output["dense_captions"].append(
                {
                    "text": caption.text,
                    "confidence": caption.confidence,
                    "bounding_box": bounding_box_to_dict(caption.bounding_box),
                }
            )

    return output


def main() -> None:
    result = analyze_caption("sample.jpg")
    save_json(result, "caption_results.json")
    print(result)


if __name__ == "__main__":
    main()