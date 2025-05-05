import os
from PyPDF2 import PdfReader
import ebooklib
from ebooklib import epub
import pytesseract
from PIL import Image
import pdf2image

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return ""

def extract_text_from_epub(epub_path):
    try:
        book = epub.read_epub(epub_path)
        content = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content.append(item.get_body_content().decode("utf-8"))
        return " ".join(content)
    except Exception as e:
        print(f"❌ Error extracting text from EPUB: {e}")
        return ""

def ocr_text_extractor(pdf_path):
    try:
        images = pdf2image.convert_from_path(pdf_path)
        ocr_text = ""
        for image in images:
            ocr_text += pytesseract.image_to_string(image, lang='eng+san')
        return ocr_text.strip()
    except Exception as e:
        print(f"❌ Error running OCR on PDF: {e}")
        return ""