"""
DELTA PROCESSING - TRACK CHANGES BETWEEN RUNS
"""

import os
import json

def get_existing_checksums(json_dir):
    """
    LOAD EXISTING RECORDS FOR CHANGE DETECTION
    RETURNS: {checksum: document_id} mapping
    """
    existing = {}
    if not os.path.exists(json_dir):
        return existing
        
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(json_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing[data["checksum"]] = data["document_id"]
            except:
                continue
    return existing

def is_new_or_updated(checksum, existing_checksums):
    """CHECK IF DOCUMENT IS NEW OR MODIFIED"""
    return checksum not in existing_checksums