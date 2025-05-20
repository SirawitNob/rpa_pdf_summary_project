import os
import pandas as pd
import requests
import base64
import fitz  # PyMuPDF
from openpyxl import load_workbook
import openai
import re
import pdfplumber

# === CONFIGURATION ===
EXCEL_INPUT_FILE = "input_excel.xlsx"
SHEET_NAME = "Sheet1"
LINK_COLUMN = "Link"
OUTPUT_SUMMARY_COLUMN = "Summarize"
TEMP_PDF_DIR = "pdf_files"
EXCEL_OUTPUT_FILE = "output_with_blob_and_summary.xlsx"

# Set your OpenAI API Key
openai.api_key = ""


def download_pdf(url, save_path):
    url = convert_google_drive_url(url)
    try:
        response = requests.get(url, timeout=15)
        content_type = response.headers.get("Content-Type", "")
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download PDF: {url} (status {response.status_code})")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def convert_google_drive_url(url):
    match = re.match(r"https://drive\.google\.com/file/d/([^/]+)/view", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

def pdf_to_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""


from openai import OpenAI

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

def extract_text_from_pdf_page_range(file_path, start_page, end_page):
    try:
        with pdfplumber.open(file_path) as pdf:
            max_page = len(pdf.pages)
            # Clip the range to avoid IndexError
            start = max(1, start_page)
            end = min(end_page, max_page)

            text = ""
            for page_num in range(start - 1, end):
                page_text = pdf.pages[page_num].extract_text()
                if page_text:
                    text += page_text + "\n\n"
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from page range {start_page}-{end_page}: {e}")
        return ""

def main():
    if not os.path.exists(TEMP_PDF_DIR):
        os.makedirs(TEMP_PDF_DIR)

    df = pd.read_excel(EXCEL_INPUT_FILE, sheet_name=SHEET_NAME, engine="openpyxl")
    df[OUTPUT_SUMMARY_COLUMN] = df[OUTPUT_SUMMARY_COLUMN].astype("object")

    for idx, row in df.iterrows():
        url = row.get(LINK_COLUMN)
        if isinstance(url, str) and url.startswith("http"):
            print(f"Processing row {idx + 2} | URL: {url}")
            filename = f"{TEMP_PDF_DIR}/file_{idx}.pdf"
            if download_pdf(url, filename):
                summary = summarize_text_with_gpt_from_pages(filename, 40, 50)
                print(summary)

                df.at[idx, OUTPUT_SUMMARY_COLUMN] = summary

    df.to_excel(EXCEL_OUTPUT_FILE, index=False, sheet_name=SHEET_NAME, engine="openpyxl")
    print(f"\n✅ Completed. Output saved to: {EXCEL_OUTPUT_FILE}")


main()
