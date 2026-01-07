from pypdf import PdfReader

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file"""
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
