import json
import os
from pathlib import Path
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
SAMPLE_PATH = BASE_DIR / "sample-data" / "language_samples.json"
OUTPUT_PATH = BASE_DIR / "outputs" / "key_phrase_results.json"

def create_client() -> TextAnalyticsClient:
    load_dotenv()
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    key = os.getenv("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError(
            "AZURE_LANGUAGE_ENDPOINT 또는 AZURE_LANGUAGE_KEY가 설정되지 않았습니다. "
            "루트 폴더의 .env 파일을 확인하세요."
        )

    return TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

def load_documents() -> list[dict]:
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["documents"]

def extract_key_phrases() -> list[dict]:
    client = create_client()
    documents = load_documents()
    results = client.extract_key_phrases(documents=documents)

    output = []

    for doc, result in zip(documents, results):
        item = {
            "id": doc["id"],
            "text": doc["text"],
            "key_phrases": []
        }

        if result.is_error:
            item["error"] = {
                "code": result.error.code,
                "message": result.error.message
            }
        else:
            item["key_phrases"] = list(result.key_phrases)

        output.append(item)

    return output

def save_results(results: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def main() -> None:
    results = extract_key_phrases()
    save_results(results)
    print(f"핵심 구 추출 완료: {OUTPUT_PATH}")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()