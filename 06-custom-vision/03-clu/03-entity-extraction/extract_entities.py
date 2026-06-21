import os
import requests
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
KEY = os.getenv("AZURE_LANGUAGE_KEY")
PROJECT_NAME = os.getenv("AZURE_CLU_PROJECT_NAME")
DEPLOYMENT_NAME = os.getenv("AZURE_CLU_DEPLOYMENT_NAME", "production")

API_VERSION = "2023-04-01"


def analyze_conversation(text: str) -> dict:
    if not text or not text.strip():
        return {"error": "분석할 문장을 입력하세요."}

    if not ENDPOINT or not KEY or not PROJECT_NAME or not DEPLOYMENT_NAME:
        return {"error": "환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요."}

    url = f"{ENDPOINT.rstrip('/')}/language/:analyze-conversations?api-version={API_VERSION}"

    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Content-Type": "application/json"
    }

    body = {
        "kind": "Conversation",
        "analysisInput": {
            "conversationItem": {
                "id": "1",
                "participantId": "user",
                "text": text
            }
        },
        "parameters": {
            "projectName": PROJECT_NAME,
            "deploymentName": DEPLOYMENT_NAME,
            "stringIndexType": "TextElement_V8"
        }
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code >= 400:
        return {
            "error": response.text,
            "status_code": response.status_code
        }

    return response.json()


def get_top_intent(result: dict) -> dict:
    try:
        prediction = result["result"]["prediction"]
        return {
            "top_intent": prediction.get("topIntent"),
            "intents": prediction.get("intents", [])
        }
    except KeyError:
        return {
            "top_intent": None,
            "intents": []
        }


def get_entities(result: dict) -> list:
    try:
        prediction = result["result"]["prediction"]
        return prediction.get("entities", [])
    except KeyError:
        return []