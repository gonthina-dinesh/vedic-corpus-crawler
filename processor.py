"""
DOCUMENT PROCESSOR - TRANSFORMS FILES TO STRUCTURED METADATA
"""

import os
import hashlib
import datetime
from metadata_extractor import extract_metadata_from_pdf

def process_document(filepath):
    """
    PROCESS INDIVIDUAL DOCUMENT INTO STANDARDIZED JSON
    HANDLES:
    - Checksum generation
    - Metadata extraction
    - Result validation
    """
    if not os.path.exists(filepath):
        print(f"❌ FILE NOT FOUND: {filepath}")
        return None
        
    try:
        # GENERATE FILE FINGERPRINT
        checksum = compute_sha256(filepath)
        doc_id = generate_document_id(checksum)
        
        # EXTRACT METADATA (PDF-SPECIFIC)
        if filepath.lower().endswith('.pdf'):
            metadata = extract_metadata_from_pdf(filepath)
        else:
            metadata = {"title": os.path.basename(filepath)}
        
        # VALIDATE AND FORMAT RESULTS
        if not metadata.get("title"):
            metadata["title"] = os.path.basename(filepath)
            
        return {
            "document_id": doc_id,
            "checksum": checksum,
            "title": metadata["title"],
            "authors": metadata.get("authors", []),
            "pub_year": metadata.get("pub_year"),
            "language": metadata.get("language", "Unknown"),
            "scraped_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        print(f"❌ PROCESSING FAILED: {filepath}\nError: {str(e)}")
        return None

# UTILITY FUNCTIONS
def compute_sha256(filepath):
    """GENERATE CRYPTOGRAPHIC FILE HASH"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_document_id(checksum):
    """CREATE SHORT UNIQUE ID FROM CHECKSUM"""
    return checksum[:12]