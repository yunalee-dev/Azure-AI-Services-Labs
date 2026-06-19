from common import analyze_document, save_json, print_content

file_path = "../sample-data/database_basic.pdf"

result = analyze_document(
    model_id="prebuilt-layout",
    file_path=file_path
)

save_json(result, "../outputs/layout_result.json")

print_content(result)

tables = result.get("analyzeResult", {}).get("tables", [])

print(f"\n추출된 표 개수: {len(tables)}")

for table_idx, table in enumerate(tables):
    print(f"\n[Table {table_idx + 1}]")
    print(f"rows: {table.get('rowCount')}, columns: {table.get('columnCount')}")

    for cell in table.get("cells", []):
        row = cell.get("rowIndex")
        col = cell.get("columnIndex")
        text = cell.get("content")
        print(f"({row}, {col}) {text}")