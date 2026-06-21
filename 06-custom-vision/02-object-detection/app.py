import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from msrest.authentication import ApiKeyCredentials
from PIL import Image, ImageDraw

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient


BASE_DIR = Path(__file__).resolve().parents[1]   # 06-custom-vision
ROOT_DIR = Path(__file__).resolve().parents[2]   # azure-ai-services-labs
ENV_PATH = ROOT_DIR / ".env"

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


trainer, predictor = create_clients()


def get_project_by_name():
    for project in trainer.get_projects():
        if project.name == PROJECT_NAME:
            return project

    raise RuntimeError(
        f"프로젝트를 찾을 수 없습니다: {PROJECT_NAME}\n"
        "먼저 train_detection.py를 실행해서 객체 감지 프로젝트를 생성하고 학습해야 합니다."
    )


project = get_project_by_name()


def detect_image(image_path):
    if image_path is None:
        return None

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    response = predictor.detect_image(
        project_id=project.id,
        published_name=PUBLISH_NAME,
        image_data=image_data,
    )

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    img_width, img_height = image.size

    for prediction in response.predictions:
        if prediction.probability < 0.5:
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

    return image


demo = gr.Interface(
    fn=detect_image,
    inputs=gr.Image(type="filepath", label="객체 감지할 이미지 업로드"),
    outputs=gr.Image(type="pil", label="객체 감지 결과"),
    title="Custom Vision Object Detection",
    description="포크와 가위 위치를 감지하고 Bounding Box를 표시합니다.",
)

if __name__ == "__main__":
    print("ENV_PATH:", ENV_PATH)
    demo.launch()