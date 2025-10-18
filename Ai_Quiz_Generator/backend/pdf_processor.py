import pdfplumber
from io import BytesIO

class PDFProcessor:
    def extract_text(self, file_bytes):
        """Extract text from PDF bytes"""
        text = ""
        try:
            with BytesIO(file_bytes) as byte_stream:
                with pdfplumber.open(byte_stream) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        if len(text) > 10000:
                            break
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text