import os
import json
from pathlib import Path

from dotenv import load_dotenv
from msrest.authentication import ApiKeyCredentials
from PIL import Image, ImageDraw

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient


BASE_DIR = Path(__file__).resolve().parents[1]   # 06-custom-vision
ROOT_DIR = Path(__file__).resolve().parents[2]   # azure-ai-services-labs
ENV_PATH = ROOT_DIR / ".env"

TEST_IMAGE_PATH = BASE_DIR / "sample-data" / "detection" / "test" / "test_image.jpg"
OUTPUT_DIR = BASE_DIR / "outputs" / "detection-results"

PROJECT_NAME = "fork-scissors-object-detection"
PUBLISH_NAME = "fork-scissors-detection-v1"


def load_env():
    if not ENV_PATH.exists():
        raise FileNotFoundError(f".env 파일을 찾을 수 없습니다: {ENV_PATH}")

    load_dotenv(ENV_PATH)

    required_keys = [
        "TRAINING_ENDPOINT",
        "TRAINING_API_KEY",
        "PREDICTION_ENDPOINT",
        "PREDICTION_API_KEY",
    ]

    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        raise ValueError(f".env 파일에 다음 값이 없습니다: {', '.join(missing_keys)}")


def create_clients():
    load_env()

    training_credentials = ApiKeyCredentials(
        in_headers={"Training-key": os.getenv("TRAINING_API_KEY")}
    )

    prediction_credentials = ApiKeyCredentials(
        in_headers={"Prediction-key": os.getenv("PREDICTION_API_KEY")}
    )

    trainer = CustomVisionTrainingClient(
        endpoint=os.getenv("TRAINING_ENDPOINT"),
        credentials=training_credentials,
    )

    predictor = CustomVisionPredictionClient(
        endpoint=os.getenv("PREDICTION_ENDPOINT"),
        credentials=prediction_credentials,
    )

    return trainer, predictor


def get_project_by_name(trainer):
    for project in trainer.get_projects():
        if project.name == PROJECT_NAME:
            return project

    raise RuntimeError(
        f"프로젝트를 찾을 수 없습니다: {PROJECT_NAME}\n"
        "먼저 train_detection.py를 실행해서 객체 감지 프로젝트를 생성하고 학습해야 합니다."
    )


def draw_predictions(image_path, predictions, threshold=0.5):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    img_width, img_height = image.size
    result_data = []

    for prediction in predictions:
        if prediction.probability < threshold:
            continue

        box = prediction.bounding_box

        left = box.left * img_width
        top = box.top * img_height
        width = box.width * img_width
        height = box.height * img_height

        label = f"{prediction.tag_name} {prediction.probability * 100:.1f}%"

        draw.rectangle(
            [(left, top), (left + width, top + height)],
            outline="green",
            width=3,
        )

        draw.text(
            (left, max(top - 14, 0)),
            label,
            fill="green",
        )

        result_data.append(
            {
                "tag": prediction.tag_name,
                "probability": prediction.probability,
                "bounding_box": {
                    "left": box.left,
                    "top": box.top,
                    "width": box.width,
                    "height": box.height,
                },
            }
        )

    return image, result_data


def main():
    print("ENV_PATH:", ENV_PATH)
    print("TEST_IMAGE_PATH:", TEST_IMAGE_PATH)

    if not TEST_IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"테스트 이미지를 찾을 수 없습니다: {TEST_IMAGE_PATH}\n"
            "sample-data/detection/test/test_image.jpg 위치에 테스트 이미지를 넣어 주세요."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    trainer, predictor = create_clients()
    project = get_project_by_name(trainer)

    with open(TEST_IMAGE_PATH, "rb") as image_file:
        image_data = image_file.read()

    response = predictor.detect_image(
        project_id=project.id,
        published_name=PUBLISH_NAME,
        image_data=image_data,
    )

    result_image, result_data = draw_predictions(
        TEST_IMAGE_PATH,
        response.predictions,
    )

    result_image_path = OUTPUT_DIR / "test_result_with_box.png"
    result_json_path = OUTPUT_DIR / "test_result.json"

    result_image.save(result_image_path)

    with open(result_json_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, ensure_ascii=False, indent=2)

    print("예측 결과 이미지 저장:", result_image_path)
    print("예측 결과 JSON 저장:", result_json_path)


if __name__ == "__main__":
    main()