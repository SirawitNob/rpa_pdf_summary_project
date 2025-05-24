import requests
MODEL_NAME = "llama3.1"
from pdf_utils import extract_text_from_pdf_page_range

def summarize_with_llama(file_path, start_page=43, end_page=43, model=MODEL_NAME):
    text = extract_text_from_pdf_page_range(file_path, start_page, end_page)
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "From the table in the following content, extract only the data for (Trustee fee / ค่าธรรมเนียมผู้ดูแลผลประโยชน์). Return the result in a structured format."},
                    {"role": "user", "content": f"Summarize the Trustee fee data from pages {start_page}-{end_page} of the PDF content:\n\n{text}"}
                ],
                "stream": False
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "[No response]")
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "[Error summarizing]"