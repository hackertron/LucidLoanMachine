import requests
import os
import PyPDF2
from typing import Annotated
from urllib.parse import urlparse

def download_pdf(url: Annotated[str, "the pdf file url"]) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")
    filename = os.path.basename(urlparse(url).path)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

def extract_text_from_pdf(pdf_file: Annotated[str, "the local pdf file path"], password: Annotated[str, "PDF password (optional)"] = None) -> str:
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        if reader.is_encrypted:
            if password is None:
                raise ValueError("The PDF is encrypted and requires a password.")
            try:
                reader.decrypt(password)
            except:
                raise ValueError("Incorrect password for the PDF.")

        return "".join(page.extract_text() for page in reader.pages)

def process_pdf_from_url(url: Annotated[str, "the pdf file url"], password: Annotated[str, "PDF password (optional)"] = None) -> str:
    try:
        # Download the PDF
        local_file = download_pdf(url)
        print(f"PDF downloaded as: {local_file}")

        # Extract text from the downloaded PDF
        text = extract_text_from_pdf(local_file, password)

        # Clean up: remove the downloaded file
        os.remove(local_file)
        print(f"Removed temporary file: {local_file}")

        return text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

def process_local_pdf(file_path: Annotated[str, "local pdf file path"], password: Annotated[str, "PDF password (optional)"] = None) -> str:
    try:
        return extract_text_from_pdf(file_path, password)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

# Usage examples
# For a PDF from URL
# pdf_url = "http://127.0.0.1:5500/bank-statement.pdf"  # Replace with actual URL
# pdf_password = "your_password_here"  # Replace with actual password if needed
# text_from_url = process_pdf_from_url(pdf_url, pdf_password)
# print("Extracted text from URL:")
# print(text_from_url)

# # For a local PDF file
# local_pdf_path = "path/to/local/bank-statement-2.pdf"  # Replace with actual local path
# local_pdf_password = "your_local_pdf_password"  # Replace with actual password if needed
# text_from_local = process_local_pdf(local_pdf_path, local_pdf_password)
# print("Extracted text from local file:")
# print(text_from_local)