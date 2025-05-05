"""
MAIN ENTRY POINT FOR DOCUMENT HARVESTING PIPELINE
ORCHESTRATES CRAWLING, PROCESSING AND OUTPUT GENERATION
"""

from urllib.parse import urlparse
from crawler import crawl_site, START_URLS
from processor import process_document
from delta import get_existing_checksums
from utils import compute_checksum, clean_test_directories
import json
import os
import datetime

# CONFIGURATION
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
JSON_DIR = os.path.join(DATA_DIR, "json")
MAX_DOCS_PER_SITE = 10000  # Limit for testing

def main():
    """EXECUTE FULL HARVESTING WORKFLOW"""
    print("🚀 INITIALIZING DOCUMENT HARVESTER")
    
    # SETUP DIRECTORIES
    clean_test_directories()
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    
    # LOAD EXISTING RECORDS FOR DELTA PROCESSING
    existing_checksums = get_existing_checksums(JSON_DIR)
    print(f"📊 FOUND {len(existing_checksums)} EXISTING RECORDS")
    
    # PROCESS EACH TARGET SITE
    for url in START_URLS:
        print(f"\n🌐 CRAWLING: {url}")
        
        # DOWNLOAD DOCUMENTS
        downloaded_files = crawl_site(url, RAW_DIR, max_docs=MAX_DOCS_PER_SITE)
        
        # PROCESS EACH DOWNLOADED FILE
        for doc_url, filepath in downloaded_files.items():
            if not filepath.lower().endswith('.pdf'):
                print(f"⏩ SKIPPING NON-PDF: {os.path.basename(filepath)}")
                continue

            # CHECK FOR UPDATES
            checksum = compute_checksum(filepath)
            if checksum in existing_checksums:
                print(f"♻️ SKIPPING UNCHANGED: {os.path.basename(filepath)}")
                continue
                
            # PROCESS METADATA
            try:
                record = process_document(filepath)
                if not record:
                    continue
                    
                # ENHANCE RECORD WITH CONTEXT
                record.update({
                    "site": urlparse(url).netloc,
                    "download_url": doc_url
                })
                
                # SAVE OUTPUT
                output_path = os.path.join(JSON_DIR, f"{record['document_id']}.json")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(record, f, indent=2, ensure_ascii=False)
                
                print(f"✅ PROCESSED: {record['title']}")
                
            except Exception as e:
                print(f"❌ PROCESSING FAILED: {os.path.basename(filepath)} - {str(e)}")

    print("\n🏁 HARVESTING COMPLETE")

if __name__ == "__main__":
    main()