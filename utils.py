"""
UTILITY FUNCTIONS FOR FILE OPERATIONS
"""

import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path
import shutil

def is_valid_document(url):
    """CHECK IF URL POINTS TO A DOCUMENT FILE"""
    return url.lower().endswith(('.pdf', '.epub'))

def sanitize_filename(url):
    """
    CREATE SAFE FILENAME FROM URL
    CONVERTS: https://site.com/path/file.pdf → site.com_path_file.pdf
    """
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.replace('/', '_').strip('_')
    return f"{domain}_{path}" if path else domain

def save_document(url, content, download_dir):
    """SAVE DOWNLOADED CONTENT TO DISK"""
    filename = sanitize_filename(url)
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(download_dir, filename)
    
    try:
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath
    except Exception as e:
        print(f"❌ SAVE FAILED: {filename}\nError: {str(e)}")
        return None

def compute_checksum(filepath):
    """GENERATE SHA256 CHECKSUM FOR FILE"""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"⚠️ CHECKSUM FAILED: {filepath}\nError: {str(e)}")
        return ""

def clean_test_directories():
    """RESET OUTPUT DIRECTORIES FOR TESTING"""
    dirs = ["data/raw", "data/json"]
    for dirpath in dirs:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.makedirs(dirpath)
    print("🧹 CLEANED TEST DIRECTORIES")