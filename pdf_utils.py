import requests
import base64
import re
import pdfplumber

def download_pdf(url, save_path):
    url = convert_google_drive_url(url)
    try:
        response = requests.get(url, timeout=15)
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