import argparse
import json
import os
import uuid
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
SAMPLE_PATH = BASE_DIR / "sample-data" / "language_samples.json"
OUTPUT_PATH = BASE_DIR / "outputs" / "translation_results.json"

def load_translation_samples() -> list[dict]:
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["translation_samples"]

def translate_texts(target_language: str, source_language: str | None = None) -> list[dict]:
    load_dotenv()
    endpoint = os.getenv(
        "AZURE_TRANSLATOR_ENDPOINT",
        "https://api.cognitive.microsofttranslator.com"
    )
    key = os.getenv("AZURE_TRANSLATOR_KEY")
    region = os.getenv("AZURE_TRANSLATOR_REGION")

    if not key:
        raise ValueError(
            "AZURE_TRANSLATOR_KEY가 설정되지 않았습니다. "
            "루트 폴더의 .env 파일을 확인하세요."
        )

    route = "/translate"
    params = {
        "api-version": "3.0",
        "to": target_language
    }

    if source_language:
        params["from"] = source_language

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }

    if region:
        headers["Ocp-Apim-Subscription-Region"] = region

    samples = load_translation_samples()
    body = [{"text": sample["text"]} for sample in samples]

    response = requests.post(
        endpoint + route,
        params=params,
        headers=headers,
        json=body,
        timeout=30
    )

    response.raise_for_status()

    translated = response.json()

    output = []

    for sample, result in zip(samples, translated):
        item = {
            "id": sample["id"],
            "original_text": sample["text"],
            "translations": []
        }

        for translation in result.get("translations", []):
            item["translations"].append({
                "to": translation.get("to"),
                "text": translation.get("text")
            })

        output.append(item)

    return output

def save_results(results: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Azure Translator REST API로 텍스트를 번역합니다."
    )
    parser.add_argument(
        "--to",
        default="ko",
        help="번역할 대상 언어 코드입니다. 예: ko, en, ja, es"
    )
    parser.add_argument(
        "--from-lang",
        default=None,
        help="원본 언어 코드입니다. 생략하면 자동 감지합니다."
    )
    args = parser.parse_args()

    results = translate_texts(
        target_language=args.to,
        source_language=args.from_lang
    )
    save_results(results)

    print(f"번역 완료: {OUTPUT_PATH}")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()