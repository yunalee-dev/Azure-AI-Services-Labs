# 05-ai-vision/common_vision.py

import json
import os
from pathlib import Path
from typing import Any

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample-data"
OUTPUT_DIR = BASE_DIR / "outputs"


def create_vision_client() -> ImageAnalysisClient:
    """
    .env 파일에서 Azure AI Vision Endpoint와 Key를 읽어
    ImageAnalysisClient 객체를 생성한다.
    """
    load_dotenv()

    endpoint = os.getenv("AZURE_VISION_ENDPOINT")
    key = os.getenv("AZURE_VISION_KEY")

    if not endpoint:
        raise ValueError(
            "AZURE_VISION_ENDPOINT가 설정되지 않았습니다. "
            "루트 폴더의 .env 파일을 확인하세요."
        )

    if not key:
        raise ValueError(
            "AZURE_VISION_KEY가 설정되지 않았습니다. "
            "루트 폴더의 .env 파일을 확인하세요."
        )

    return ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


def load_image_bytes(image_name: str = "sample.jpg") -> bytes:
    """
    sample-data 폴더에 있는 이미지를 bytes 형태로 읽는다.
    Azure AI Vision SDK는 이미지 파일을 bytes로 전달할 수 있다.
    """
    image_path = SAMPLE_DIR / image_name

    if not image_path.exists():
        raise FileNotFoundError(
            f"이미지 파일을 찾을 수 없습니다: {image_path}\n"
            f"05-ai-vision/sample-data/ 폴더에 {image_name} 파일을 넣어주세요."
        )

    with open(image_path, "rb") as image_file:
        return image_file.read()


def save_json(data: dict[str, Any], output_name: str) -> Path:
    """
    분석 결과를 outputs 폴더에 JSON 파일로 저장한다.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / output_name

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"저장 완료: {output_path}")
    return output_path


def bounding_box_to_dict(bounding_box: Any) -> dict[str, int] | None:
    """
    Azure Vision SDK의 bounding_box 객체를 dict로 변환한다.
    """
    if bounding_box is None:
        return None

    return {
        "x": bounding_box.x,
        "y": bounding_box.y,
        "width": bounding_box.width,
        "height": bounding_box.height,
    }


def polygon_to_list(points: Any) -> list[dict[str, int]]:
    """
    OCR 결과의 bounding polygon 좌표를 list[dict] 형태로 변환한다.
    """
    if not points:
        return []

    return [{"x": point.x, "y": point.y} for point in points]