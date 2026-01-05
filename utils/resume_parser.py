from pypdf import PdfReader

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file.
    Args:
        pdf_file: Uploaded file object (Streamlit file_uploader) or local PDF path
    Returns:
        str: extracted text
    """
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text