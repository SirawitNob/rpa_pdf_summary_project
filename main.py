import os
import pandas as pd

from pdf_utils import download_pdf
from llama_utils import summarize_with_llama
# === CONFIGURATION ===
EXCEL_INPUT_FILE = "input_excel.xlsx"
SHEET_NAME = "Sheet1"
LINK_COLUMN = "Link"
OUTPUT_SUMMARY_COLUMN = "Summarize"
TEMP_PDF_DIR = "pdf_files"
EXCEL_OUTPUT_FILE = "output_with_blob_and_summary.xlsx"

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
                summary = summarize_with_llama(filename, 42, 45)
                print(summary)

                df.at[idx, OUTPUT_SUMMARY_COLUMN] = summary

    df.to_excel(EXCEL_OUTPUT_FILE, index=False, sheet_name=SHEET_NAME, engine="openpyxl")
    print(f"\n✅ Completed. Output saved to: {EXCEL_OUTPUT_FILE}")


main()
