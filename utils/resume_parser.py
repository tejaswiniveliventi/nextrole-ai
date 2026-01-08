from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        logger.info("Extracted text from PDF (chars=%d)", len(text))
        return text
    except Exception as e:
        logger.exception("Failed to extract text from PDF: %s", e)
        return ""
