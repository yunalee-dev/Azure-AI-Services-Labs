import os
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from msrest.authentication import ApiKeyCredentials

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch,
    ImageFileCreateEntry,
    Region,
)


BASE_DIR = Path(__file__).resolve().parents[1]   # 06-custom-vision
ROOT_DIR = Path(__file__).resolve().parents[2]   # azure-ai-services-labs
ENV_PATH = ROOT_DIR / ".env"

DATA_DIR = BASE_DIR / "sample-data" / "detection"
LABEL_PATH = BASE_DIR / "sample-data" / "labels" / "detection_regions.json"

PROJECT_NAME = "fork-scissors-object-detection"
PROJECT_DESCRIPTION = "포크와 가위를 이미지 안에서 감지하는 Custom Vision 객체 감지 모델"
PUBLISH_NAME = "fork-scissors-detection-v1"


def load_env():
    if not ENV_PATH.exists():
        raise FileNotFoundError(f".env 파일을 찾을 수 없습니다: {ENV_PATH}")

    load_dotenv(ENV_PATH)

    required_keys = [
        "TRAINING_ENDPOINT",
        "TRAINING_API_KEY",
        "PREDICTION_RESOURCE_ID",
    ]

    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        raise ValueError(f".env 파일에 다음 값이 없습니다: {', '.join(missing_keys)}")


def create_trainer():
    load_env()

    training_credentials = ApiKeyCredentials(
        in_headers={"Training-key": os.getenv("TRAINING_API_KEY")}
    )

    return CustomVisionTrainingClient(
        endpoint=os.getenv("TRAINING_ENDPOINT"),
        credentials=training_credentials,
    )


def get_detection_domain_id(trainer):
    for domain in trainer.get_domains():
        if domain.type == "ObjectDetection" and domain.name == "General (compact)":
            return domain.id

    for domain in trainer.get_domains():
        if domain.type == "ObjectDetection" and domain.name == "General":
            return domain.id

    raise RuntimeError("Object Detection 도메인을 찾을 수 없습니다.")


def get_or_create_project(trainer):
    for project in trainer.get_projects():
        if project.name == PROJECT_NAME:
            print("기존 객체 감지 프로젝트를 사용합니다.")
            return project

    domain_id = get_detection_domain_id(trainer)

    print("새 객체 감지 프로젝트를 생성합니다.")
    return trainer.create_project(
        name=PROJECT_NAME,
        description=PROJECT_DESCRIPTION,
        domain_id=domain_id,
    )


def get_or_create_tag(trainer, project_id, tag_name):
    tags = trainer.get_tags(project_id)

    for tag in tags:
        if tag.name == tag_name:
            print(f"기존 태그 사용: {tag_name}")
            return tag

    print(f"새 태그 생성: {tag_name}")
    return trainer.create_tag(project_id, tag_name)


def load_region_labels():
    if not LABEL_PATH.exists():
        raise FileNotFoundError(
            f"라벨 파일이 없습니다: {LABEL_PATH}\n"
            "먼저 make_detection_regions.py를 실행해서 "
            "sample-data/labels/detection_regions.json 파일을 만들어 주세요."
        )

    with open(LABEL_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def make_image_entries(label_data, tag_map):
    image_entries = []

    for tag_name, images in label_data.items():
        if tag_name not in tag_map:
            print(f"알 수 없는 태그라 건너뜀: {tag_name}")
            continue

        tag = tag_map[tag_name]

        for image_name, box in images.items():
            image_path = DATA_DIR / tag_name / image_name

            if not image_path.exists():
                print(f"이미지 파일 없음: {image_path}")
                continue

            if len(box) != 4:
                print(f"잘못된 박스 형식: {image_name} -> {box}")
                continue

            left, top, width, height = box

            region = Region(
                tag_id=tag.id,
                left=left,
                top=top,
                width=width,
                height=height,
            )

            with open(image_path, "rb") as image_file:
                image_entries.append(
                    ImageFileCreateEntry(
                        name=image_name,
                        contents=image_file.read(),
                        regions=[region],
                    )
                )

    print(f"업로드 준비 이미지 수: {len(image_entries)}")
    return image_entries


def upload_training_images(trainer, project, image_entries):
    if not image_entries:
        raise RuntimeError(
            "업로드할 이미지가 없습니다.\n"
            f"이미지 폴더 확인: {DATA_DIR}\n"
            f"라벨 파일 확인: {LABEL_PATH}"
        )

    upload_result = trainer.create_images_from_files(
        project_id=project.id,
        batch=ImageFileCreateBatch(images=image_entries),
    )

    if upload_result.is_batch_successful:
        print("이미지 업로드 성공")
    else:
        print("이미지 업로드 중 일부 실패")
        for image in upload_result.images:
            print(image.name, image.status)


def train_model(trainer, project):
    print("모델 학습 시작")
    iteration = trainer.train_project(project.id)

    while iteration.status != "Completed":
        iteration = trainer.get_iteration(project.id, iteration.id)
        print("학습 상태:", iteration.status)
        time.sleep(5)

    print("모델 학습 완료")
    return iteration


def publish_model(trainer, project, iteration):
    prediction_resource_id = os.getenv("PREDICTION_RESOURCE_ID")

    iterations = trainer.get_iterations(project.id)

    for item in iterations:
        if item.publish_name == PUBLISH_NAME:
            print(f"이미 게시된 모델입니다: {PUBLISH_NAME}")
            return

    trainer.publish_iteration(
        project_id=project.id,
        iteration_id=iteration.id,
        publish_name=PUBLISH_NAME,
        prediction_id=prediction_resource_id,
    )

    print(f"모델 게시 완료: {PUBLISH_NAME}")


def main():
    print("ENV_PATH:", ENV_PATH)
    print("DATA_DIR:", DATA_DIR)
    print("LABEL_PATH:", LABEL_PATH)

    trainer = create_trainer()
    project = get_or_create_project(trainer)

    fork_tag = get_or_create_tag(trainer, project.id, "fork")
    scissors_tag = get_or_create_tag(trainer, project.id, "scissors")

    label_data = load_region_labels()

    tag_map = {
        "fork": fork_tag,
        "scissors": scissors_tag,
    }

    image_entries = make_image_entries(label_data, tag_map)
    upload_training_images(trainer, project, image_entries)

    iteration = train_model(trainer, project)
    publish_model(trainer, project, iteration)


if __name__ == "__main__":
    main()