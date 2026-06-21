import os
import time
from pathlib import Path

from dotenv import load_dotenv
from msrest.authentication import ApiKeyCredentials

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import (
    ImageFileCreateBatch,
    ImageFileCreateEntry,
)


BASE_DIR = Path(__file__).resolve().parents[1]   # 06-custom-vision
ROOT_DIR = Path(__file__).resolve().parents[2]   # azure-ai-services-labs

ENV_PATH = ROOT_DIR / ".env"
DATA_DIR = BASE_DIR / "sample-data" / "classification"

PROJECT_NAME = "fork-scissors-classification"
PROJECT_DESCRIPTION = "포크와 가위를 이미지 전체 기준으로 분류하는 Custom Vision 모델"
PUBLISH_NAME = "fork-scissors-classification-v1"


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

    training_endpoint = os.getenv("TRAINING_ENDPOINT")
    training_key = os.getenv("TRAINING_API_KEY")

    credentials = ApiKeyCredentials(
        in_headers={"Training-key": training_key}
    )

    return CustomVisionTrainingClient(
        endpoint=training_endpoint,
        credentials=credentials,
    )


def get_classification_domain_id(trainer):
    for domain in trainer.get_domains():
        if domain.type == "Classification" and domain.name == "General (compact)":
            return domain.id

    for domain in trainer.get_domains():
        if domain.type == "Classification" and domain.name == "General":
            return domain.id

    raise RuntimeError("Classification 도메인을 찾을 수 없습니다.")


def get_or_create_project(trainer):
    for project in trainer.get_projects():
        if project.name == PROJECT_NAME:
            print("기존 이미지 분류 프로젝트를 사용합니다.")
            return project

    domain_id = get_classification_domain_id(trainer)

    print("새 이미지 분류 프로젝트를 생성합니다.")
    return trainer.create_project(
        name=PROJECT_NAME,
        description=PROJECT_DESCRIPTION,
        domain_id=domain_id,
        classification_type="Multiclass",
    )


def get_or_create_tag(trainer, project_id, tag_name):
    tags = trainer.get_tags(project_id)

    for tag in tags:
        if tag.name == tag_name:
            print(f"기존 태그 사용: {tag_name}")
            return tag

    print(f"새 태그 생성: {tag_name}")
    return trainer.create_tag(project_id, tag_name)


def load_images_for_tag(folder_path, tag_id):
    image_entries = []

    if not folder_path.exists():
        print(f"이미지 폴더가 없습니다: {folder_path}")
        return image_entries

    for image_path in sorted(folder_path.glob("*")):
        if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue

        with open(image_path, "rb") as image_file:
            image_entries.append(
                ImageFileCreateEntry(
                    name=image_path.name,
                    contents=image_file.read(),
                    tag_ids=[tag_id],
                )
            )

    print(f"{folder_path.name} 이미지 {len(image_entries)}개 로드")
    return image_entries


def upload_training_images(trainer, project, fork_tag, scissors_tag):
    image_entries = []

    image_entries.extend(
        load_images_for_tag(DATA_DIR / "fork", fork_tag.id)
    )

    image_entries.extend(
        load_images_for_tag(DATA_DIR / "scissors", scissors_tag.id)
    )

    if not image_entries:
        raise RuntimeError(
            "업로드할 이미지가 없습니다.\n"
            f"다음 폴더를 확인해 주세요:\n{DATA_DIR / 'fork'}\n{DATA_DIR / 'scissors'}"
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

    trainer = create_trainer()

    project = get_or_create_project(trainer)

    fork_tag = get_or_create_tag(trainer, project.id, "fork")
    scissors_tag = get_or_create_tag(trainer, project.id, "scissors")

    upload_training_images(trainer, project, fork_tag, scissors_tag)

    iteration = train_model(trainer, project)

    publish_model(trainer, project, iteration)


if __name__ == "__main__":
    main()