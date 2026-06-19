from common import analyze_document, save_json, print_content


file_path = "../sample-data/receipt.jpg"

result = analyze_document(
    model_id="prebuilt-invoice",
    file_path=file_path
)

save_json(result, "../outputs/invoice_result.json")

print_content(result)


documents = result.get("analyzeResult", {}).get("documents", [])

for doc_idx, document in enumerate(documents):
    print(f"\n[Invoice Document {doc_idx + 1}]")

    fields = document.get("fields", {})

    for field_name, field_data in fields.items():
        value = field_data.get("content")
        confidence = field_data.get("confidence")

        print(f"{field_name}: {value} / confidence={confidence}")