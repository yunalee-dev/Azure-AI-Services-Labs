# 05-ai-vision/02-ocr/analyze_ocr.py

import sys
from pathlib import Path

from azure.ai.vision.imageanalysis.models import VisualFeatures

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common_vision import (
    create_vision_client,
    load_image_bytes,
    polygon_to_list,
    save_json,
)


def analyze_ocr(image_name: str = "sample.jpg") -> dict:
    """
    이미지 속 텍스트를 OCR로 추출한다.
    Azure AI Vision에서는 OCR 기능을 VisualFeatures.READ로 요청한다.
    """
    client = create_vision_client()
    image_data = load_image_bytes(image_name)

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.READ],
    )

    output = {
        "image_name": image_name,
        "lines": [],
    }

    if result.read is not None and result.read.blocks:
        for block in result.read.blocks:
            for line in block.lines:
                line_data = {
                    "text": line.text,
                    "bounding_polygon": polygon_to_list(line.bounding_polygon),
                    "words": [],
                }

                for word in line.words:
                    line_data["words"].append(
                        {
                            "text": word.text,
                            "confidence": word.confidence,
                            "bounding_polygon": polygon_to_list(word.bounding_polygon),
                        }
                    )

                output["lines"].append(line_data)

    return output


def main() -> None:
    result = analyze_ocr("sample.jpg")
    save_json(result, "ocr_results.json")
    print(result)


if __name__ == "__main__":
    main()