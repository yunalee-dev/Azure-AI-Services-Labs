from common import analyze_document, save_json, print_content


file_path = "../sample-data/database_basic.pdf"

result = analyze_document(
    model_id="prebuilt-read",
    file_path=file_path
)

save_json(result, "../outputs/read_result.json")

print_content(result)