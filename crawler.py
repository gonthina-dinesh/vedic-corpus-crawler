"""
WEB CRAWLER FOR SANSKRIT DOCUMENT COLLECTION
HANDLES POLITE CRAWLING AND DOCUMENT DOWNLOAD
"""

import os
import time
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from utils import is_valid_document, save_document

# CONFIGURATION
HEADERS = {"User-Agent": "SanskritHarvester/1.0 (research project)"}
DELAY = 1.5  # Seconds between requests
TIMEOUT = (10, 30)  # (connect, read) timeout in seconds

# TARGET SITES (ENABLE AS NEEDED)
START_URLS = [
    "https://sanskritdocuments.org/scannedbooks/asisanskritpdfs.html",
    "https://sanskritdocuments.org/scannedbooks/asiallpdfs.html",
    # "https://indianculture.gov.in/ebooks",
    # "https://ignca.gov.in/divisionss/asi-books/",
]

def crawl_site(base_url, download_dir, max_docs=3):
    """
    CRAWL A SITE AND DOWNLOAD DOCUMENTS
    RETURNS: {url: filepath} dictionary
    """
    visited = set()
    downloaded = {}
    queue = [base_url]
    
    print(f"🔍 SEARCHING FOR DOCUMENTS (MAX {max_docs})")
    
    while queue and len(downloaded) < max_docs:
        url = queue.pop(0)
        
        # SKIP PROCESSED URLS
        if url in visited:
            continue
        visited.add(url)
        
        # RESPECT ROBOTS.TXT AND DELAY
        time.sleep(DELAY)
        if not check_robots_allowed(url):
            print(f"🤖 ROBOTS.TXT BLOCKED: {url}")
            continue
            
        try:
            # FETCH PAGE CONTENT
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            
            # CHECK IF DIRECT PDF DOWNLOAD
            if is_pdf_response(response):
                saved_path = save_document(url, response.content, download_dir)
                if saved_path:
                    downloaded[url] = saved_path
                    print(f"📥 DOWNLOADED ({len(downloaded)}/{max_docs}): {url}")
                continue
                
            # PARSE LINKS FROM HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if len(downloaded) >= max_docs:
                    break
                    
                full_url = urljoin(url, link['href'])
                if full_url not in visited and is_valid_document(full_url):
                    try:
                        doc_response = requests.get(full_url, headers=HEADERS, timeout=TIMEOUT)
                        if is_pdf_response(doc_response):
                            saved_path = save_document(full_url, doc_response.content, download_dir)
                            if saved_path:
                                downloaded[full_url] = saved_path
                                print(f"📥 DOWNLOADED ({len(downloaded)}/{max_docs}): {full_url}")
                    except Exception as e:
                        print(f"⚠️ DOWNLOAD ERROR: {full_url} - {str(e)}")
                        
        except Exception as e:
            print(f"⚠️ CRAWL ERROR: {url} - {str(e)}")
    
    return downloaded

def is_pdf_response(response):
    """CHECK IF RESPONSE CONTAINS PDF CONTENT"""
    content_type = response.headers.get('content-type', '').lower()
    return 'pdf' in content_type and response.status_code == 200

def check_robots_allowed(url):
    """VERIFY ROBOTS.TXT PERMISSIONS"""
    rp = RobotFileParser()
    try:
        rp.set_url(urljoin(url, '/robots.txt'))
        rp.read()
        return rp.can_fetch(HEADERS['User-Agent'], url)
    except:
        return True  # ALLOW IF ROBOTS.TXT UNREADABLE

def is_valid_document(url):
    """IDENTIFY DOCUMENT LINKS WORTH PROCESSING"""
    parsed = urlparse(url)
    return (parsed.path.lower().endswith('.pdf') or 
            '/pdf/' in parsed.path.lower())