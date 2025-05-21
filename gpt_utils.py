import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

from pdf_utils import extract_text_from_pdf_page_range

client = OpenAI(api_key=openai.api_key)

def summarize_text_with_gpt_from_pages(file_path, start_page=43, end_page=43):
    text = extract_text_from_pdf_page_range(file_path, start_page, end_page)

    if not text.strip():
        return f"No content found in pages {start_page}-{end_page}."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "From the table in the following content, extract only the data for (Trustee fee / ค่าธรรมเนียมผู้ดูแลผลประโยชน์). Return the result in a structured format."
                },
                {
                    "role": "user",
                    "content": f"Summarize the Trustee fee data from pages {start_page}-{end_page} of the PDF content:\n\n{text}"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Failed to summarize due to API error."