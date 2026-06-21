import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from clu_service import analyze_conversation, get_top_intent


def main():
    text = input("문장을 입력하세요: ")

    result = analyze_conversation(text)

    if "error" in result:
        print("에러 발생")
        print(result)
        return

    intent_result = get_top_intent(result)

    print("\n[Top Intent]")
    print(intent_result["top_intent"])

    print("\n[All Intents]")
    for intent in intent_result["intents"]:
        print(f"- {intent['category']}: {intent['confidenceScore']:.4f}")

    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "intent_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장 완료: {output_path}")


if __name__ == "__main__":
    main()