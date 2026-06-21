import sys
import json
import shutil
from pathlib import Path

import gradio as gr

# 02-rest-api 폴더의 common.py를 가져오기 위한 경로 설정
BASE_DIR = Path(__file__).resolve().parents[1]
REST_API_DIR = BASE_DIR / "02-rest-api"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR = BASE_DIR / "sample-data" / "uploads"

sys.path.append(str(REST_API_DIR))

from common import analyze_document, save_json


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


MODEL_OPTIONS = {
    "Read - 텍스트 OCR": "prebuilt-read",
    "Layout - 문서 구조/표 추출": "prebuilt-layout",
    "Invoice - 청구서/영수증 분석": "prebuilt-invoice",
}


def extract_content(result: dict) -> str:
    """
    analyzeResult 안의 전체 텍스트를 꺼내는 함수
    """
    return result.get("analyzeResult", {}).get("content", "")


def extract_tables(result: dict) -> str:
    """
    layout 모델 결과에서 tables 정보를 보기 좋게 출력하는 함수
    """
    tables = result.get("analyzeResult", {}).get("tables", [])

    if not tables:
        return "추출된 표가 없습니다."

    lines = []
    lines.append(f"추출된 표 개수: {len(tables)}")

    for table_idx, table in enumerate(tables):
        lines.append("")
        lines.append(f"[Table {table_idx + 1}]")
        lines.append(f"rows: {table.get('rowCount')}, columns: {table.get('columnCount')}")

        for cell in table.get("cells", []):
            row = cell.get("rowIndex")
            col = cell.get("columnIndex")
            text = cell.get("content")
            lines.append(f"({row}, {col}) {text}")

    return "\n".join(lines)


def extract_invoice_fields(result: dict) -> str:
    """
    invoice 모델 결과에서 주요 필드만 보기 좋게 출력하는 함수
    """
    documents = result.get("analyzeResult", {}).get("documents", [])

    if not documents:
        return "추출된 invoice 필드가 없습니다."

    fields = documents[0].get("fields", {})

    if not fields:
        return "추출된 invoice 필드가 없습니다."

    lines = []

    for field_name, field_value in fields.items():
        content = field_value.get("content", "")
        confidence = field_value.get("confidence", "")
        value = field_value.get("valueString") or field_value.get("valueDate") or field_value.get("valueCurrency") or content

        lines.append(f"{field_name}: {value} (confidence: {confidence})")

    return "\n".join(lines)


def analyze_uploaded_file(file, model_label):
    """
    Gradio에서 업로드된 파일을 받아 Azure Document Intelligence로 분석
    """
    if file is None:
        return "파일을 업로드해주세요.", "", ""

    model_id = MODEL_OPTIONS[model_label]

    uploaded_path = Path(file.name)
    saved_file_path = UPLOAD_DIR / uploaded_path.name

    shutil.copy(uploaded_path, saved_file_path)

    result = analyze_document(
        model_id=model_id,
        file_path=str(saved_file_path)
    )

    output_file_name = f"{model_id}_result.json"
    output_path = OUTPUT_DIR / output_file_name

    save_json(result, str(output_path))

    content_text = extract_content(result)

    if model_id == "prebuilt-layout":
        detail_text = extract_tables(result)
    elif model_id == "prebuilt-invoice":
        detail_text = extract_invoice_fields(result)
    else:
        detail_text = "Read 모델은 주로 전체 텍스트 OCR 결과를 확인합니다."

    json_text = json.dumps(result, ensure_ascii=False, indent=2)

    return content_text, detail_text, json_text


with gr.Blocks(title="Azure Document Intelligence Demo") as demo:
    gr.Markdown("# Azure Document Intelligence Demo")
    gr.Markdown(
        """
        PDF 또는 이미지 파일을 업로드하고 Azure AI Document Intelligence REST API로 분석합니다.

        - Read: 문서 텍스트 OCR
        - Layout: 문서 구조, 표 추출
        - Invoice: 청구서/영수증 필드 추출
        """
    )

    with gr.Row():
        file_input = gr.File(
            label="분석할 파일 업로드",
            file_types=[".pdf", ".jpg", ".jpeg", ".png"]
        )

        model_input = gr.Dropdown(
            choices=list(MODEL_OPTIONS.keys()),
            value="Layout - 문서 구조/표 추출",
            label="분석 모델 선택"
        )

    analyze_button = gr.Button("분석 실행")

    with gr.Tab("추출 텍스트"):
        content_output = gr.Textbox(
            label="Extracted Content",
            lines=20
        )

    with gr.Tab("상세 결과"):
        detail_output = gr.Textbox(
            label="Tables or Invoice Fields",
            lines=20
        )

    with gr.Tab("Raw JSON"):
        json_output = gr.Code(
            label="Raw JSON Result",
            language="json",
            lines=25
        )

    analyze_button.click(
        fn=analyze_uploaded_file,
        inputs=[file_input, model_input],
        outputs=[content_output, detail_output, json_output]
    )


if __name__ == "__main__":
    demo.launch(share=True)