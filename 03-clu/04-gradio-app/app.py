import sys
from pathlib import Path

import gradio as gr
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from clu_service import analyze_conversation, get_top_intent, get_entities


def analyze_text(text):
    result = analyze_conversation(text)

    if "error" in result:
        return result["error"], None, None

    intent_result = get_top_intent(result)
    entities = get_entities(result)

    top_intent = intent_result["top_intent"]

    intent_rows = []
    for intent in intent_result["intents"]:
        intent_rows.append({
            "Intent": intent.get("category"),
            "Confidence": intent.get("confidenceScore")
        })

    entity_rows = []
    for entity in entities:
        entity_rows.append({
            "Entity": entity.get("category"),
            "Text": entity.get("text"),
            "Confidence": entity.get("confidenceScore")
        })

    intent_df = pd.DataFrame(intent_rows)
    entity_df = pd.DataFrame(entity_rows)

    summary = f"Top Intent: {top_intent}"

    return summary, intent_df, entity_df


with gr.Blocks() as demo:
    gr.Markdown("# Azure CLU 실습 앱")
    gr.Markdown("문장을 입력하면 Intent를 분류하고 Entity를 추출합니다.")

    input_text = gr.Textbox(
        label="사용자 문장",
        placeholder="예: 내일 서울에서 부산 가는 기차 예약해줘"
    )

    analyze_btn = gr.Button("분석하기")

    output_summary = gr.Textbox(
        label="분석 요약",
        interactive=False
    )

    output_intents = gr.Dataframe(
        label="Intent 결과"
    )

    output_entities = gr.Dataframe(
        label="Entity 결과"
    )

    analyze_btn.click(
        fn=analyze_text,
        inputs=input_text,
        outputs=[output_summary, output_intents, output_entities]
    )


if __name__ == "__main__":
    demo.launch(share=True)