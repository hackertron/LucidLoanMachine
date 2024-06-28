import PyPDF2
import requests
import hashlib
import io
def verify_bank_pdf(pdf_url):
    """
    Download a PDF from a given URL and perform basic integrity checks.
    
    Args:
    pdf_url (str): The URL of the PDF file to download and verify.
    
    Returns:
    dict: A dictionary containing verification results.
    """
    try:
        # Download the PDF
        response = requests.get(pdf_url)
        if response.status_code != 200:
            return {"success": False, "message": f"Failed to download PDF. Status code: {response.status_code}"}
        
        pdf_content = response.content
        
        # Calculate MD5 hash of the PDF
        md5_hash = hashlib.md5(pdf_content).hexdigest()
        
        # Read the PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        # Extract metadata
        metadata = pdf_reader.metadata
        
        # Check if the PDF is encrypted
        is_encrypted = pdf_reader.is_encrypted
        
        # Get the number of pages
        num_pages = len(pdf_reader.pages)
        
        # Check for digital signatures (this is a basic check and may not catch all types of signatures)
        has_signature = '/Sig' in pdf_reader.trailer['/Root'].get('/AcroForm', {}).get('/Fields', {})
        
        return {
            "success": True,
            "md5_hash": md5_hash,
            "is_encrypted": is_encrypted,
            "num_pages": num_pages,
            "has_signature": has_signature,
            "metadata": {
                "author": metadata.get('/Author', 'N/A'),
                "creator": metadata.get('/Creator', 'N/A'),
                "producer": metadata.get('/Producer', 'N/A'),
                "subject": metadata.get('/Subject', 'N/A'),
                "title": metadata.get('/Title', 'N/A'),
                "creation_date": metadata.get('/CreationDate', 'N/A'),
                "modification_date": metadata.get('/ModDate', 'N/A')
            }
        }
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}

# Example usage
# result = verify_bank_pdf("https://example.com/bank_statement.pdf")
# print(result)