import os
import time
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
API_VERSION = "2024-11-30"


def analyze_document(model_id: str, file_path: str):
    if not ENDPOINT or not KEY:
        raise ValueError("`.env`에 ENDPOINT와 KEY를 설정하세요.")

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    url = (
        f"{ENDPOINT}/documentintelligence/documentModels/"
        f"{model_id}:analyze?api-version={API_VERSION}"
    )

    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Content-Type": "application/octet-stream",
    }

    with open(file_path, "rb") as f:
        response = requests.post(url, headers=headers, data=f)

    if response.status_code != 202:
        print(response.text)
        response.raise_for_status()

    operation_location = response.headers["Operation-Location"]

    result_headers = {
        "Ocp-Apim-Subscription-Key": KEY
    }

    while True:
        result_response = requests.get(operation_location, headers=result_headers)
        result_response.raise_for_status()

        result = result_response.json()
        status = result.get("status")

        if status == "succeeded":
            return result

        if status == "failed":
            raise RuntimeError(result)

        time.sleep(1)


def save_json(data, output_path: str):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {output_path}")


def print_content(result):
    content = result.get("analyzeResult", {}).get("content", "")
    print(content)