"""
ADVANCED METADATA EXTRACTION FOR SANSKRIT PDFS
COMBINES NATIVE METADATA, TEXT ANALYSIS AND OCR
"""

import os
import re
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path

# DETECTION PATTERNS
TITLE_PATTERNS = [
    r'^(.{10,100}?)\n{2}',  # Text before double newlines
    r'[A-Z][^\n]{10,100}(?=\n)',  # Capitalized lines
    r'Title:\s*(.*?)\n'  # Explicit title markers
]
AUTHOR_PATTERNS = [
    r'by\s+([^\n]+)', 
    r'Author:\s*(.*?)\n',
    r'(?:Edited|Compiled) by\s+([^\n]+)'
]
SANSKRIT_KEYWORDS = ['संस्कृत', 'sanskrit', 'वेद', 'पुराण', 'श्लोक']

def extract_metadata_from_pdf(file_path):
    """
    EXTRACT METADATA WITH THREE-TIER FALLBACK:
    1. Native PDF metadata
    2. Text content analysis
    3. OCR for scanned pages
    """
    base_name = os.path.basename(file_path)
    metadata = {
        "title": base_name,
        "authors": [],
        "pub_year": None,
        "language": "Unknown"
    }
    
    try:
        with fitz.open(file_path) as doc:
            # TRY NATIVE METADATA FIRST
            if doc.metadata.get("title"):
                metadata["title"] = clean_text(doc.metadata["title"])
            if doc.metadata.get("author"):
                metadata["authors"] = clean_authors(doc.metadata["author"])
            
            # ANALYZE FIRST PAGE TEXT
            first_page = doc.load_page(0)
            text = first_page.get_text("text")
            
            # FALLBACK TO OCR IF LITTLE TEXT FOUND
            if len(text) < 100:  
                text = ocr_first_page(file_path)
            
            # EXTRACT FROM TEXT CONTENT
            text_metadata = extract_from_text(text)
            if text_metadata["title"] and metadata["title"] == base_name:
                metadata["title"] = text_metadata["title"]
            if text_metadata["authors"]:
                metadata["authors"] = text_metadata["authors"]
            
            # LANGUAGE DETECTION
            metadata["language"] = detect_language(text)
            
            # PUBLICATION YEAR
            metadata["pub_year"] = find_publication_year(
                doc.metadata.get("creationDate"),
                text
            )
            
    except Exception as e:
        print(f"⚠️ METADATA EXTRACTION FAILED: {file_path}\nError: {str(e)}")
    
    return metadata

# HELPER FUNCTIONS
def extract_from_text(text):
    """EXTRACT METADATA FROM TEXT USING PATTERN MATCHING"""
    results = {"title": None, "authors": []}
    
    # TITLE EXTRACTION
    for pattern in TITLE_PATTERNS:
        match = re.search(pattern, text, re.MULTILINE)
        if match and 10 <= len(match.group(1).strip()) <= 200:
            results["title"] = clean_text(match.group(1))
            break
    
    # AUTHOR EXTRACTION        
    for pattern in AUTHOR_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results["authors"] = clean_authors(match.group(1))
            break
            
    return results

def ocr_first_page(pdf_path, dpi=300):
    """PERFORM OCR ON FIRST PAGE ONLY"""
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=dpi)
        return pytesseract.image_to_string(images[0], lang='eng+san') if images else ""
    except Exception as e:
        print(f"⚠️ OCR FAILED: {pdf_path}\nError: {str(e)}")
        return ""

def detect_language(text):
    """DETERMINE LANGUAGE FROM TEXT CHARACTERS"""
    if not text:
        return "Unknown"
    
    # COUNT SANSKRIT CHARACTERS
    devanagari_chars = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    ratio = devanagari_chars / max(1, len(text))
    
    # CHECK FOR SANSKRIT KEYWORDS
    lower_text = text.lower()
    sanskrit_score = sum(kw in lower_text for kw in SANSKRIT_KEYWORDS)
    
    if ratio > 0.15 or sanskrit_score >= 2:
        return "Sanskrit"
    return "English"

def clean_text(text):
    """NORMALIZE EXTRACTED TEXT"""
    return ' '.join(text.strip().split())

def clean_authors(author_str):
    """CONVERT AUTHOR STRING TO STANDARDIZED LIST"""
    if not author_str:
        return []
    
    # SPLIT MULTIPLE AUTHORS
    authors = re.split(r'[,;]|\band\b', author_str)
    return [format_author_name(a.strip()) for a in authors if a.strip()]

def format_author_name(name):
    """STANDARDIZE NAME FORMAT: 'Last, First'"""
    if ',' in name:
        return name
    parts = name.split()
    return f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else name

def find_publication_year(creation_date, text):
    """EXTRACT YEAR FROM METADATA OR TEXT"""
    # FROM PDF CREATION DATE
    if creation_date:
        year_match = re.search(r"D:(\d{4})", creation_date)
        if year_match:
            return year_match.group(1)
    
    # FROM TEXT CONTENT
    if text:
        year_match = re.search(r"\b(19|20)\d{2}\b", text)
        if year_match:
            return year_match.group(0)
    
    return None