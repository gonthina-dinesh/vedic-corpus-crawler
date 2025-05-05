

# 📚 Sanskrit Document Harvester

An end-to-end pipeline to **automatically crawl, download, and process Sanskrit documents** from online sources. This tool extracts metadata, performs OCR on scanned PDFs, and structures the content into clean, machine-readable JSON files.

---

## 🧩 Features

* 🔍 Web crawler with polite scraping and customizable limits
* 📥 PDF downloader with delta checking to avoid reprocessing
* 🧠 Metadata extraction from both PDFs and filenames
* 🖨️ OCR support via Tesseract for scanned documents
* 🧾 Outputs structured JSON for each processed document
* 🛠️ Modular and extensible design for multiple websites

---

## 🚀 Quick Start

### 1. Install System Dependencies

#### On Ubuntu/Debian:

```bash
sudo apt install tesseract-ocr tesseract-ocr-san poppler-utils
```

### 2. Install Python Packages

```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline

```bash
# Run the full pipeline (crawl, download, extract, save)
python main.py

# Or test with limited downloads
python main.py --max-docs 2
```

---

## 📦 Output Format

Each document is saved as a JSON object like:

```json
{
  "document_id": "abc123def456",
  "checksum": "sha256_hash",
  "title": "Document Title",
  "authors": ["Last, First"],
  "pub_year": "2020",
  "language": "Sanskrit",
  "scraped_at": "2025-05-05T12:00:00Z",
  "download_url": "https://example.com/original.pdf"
}
```

---

## ⚙️ Configuration

Customize behavior via the following scripts:

| File                    | Purpose                               |
| ----------------------- | ------------------------------------- |
| `crawler.py`            | Set `START_URLS`, delay, crawl logic  |
| `main.py`               | Limit max docs with `--max-docs` flag |
| `delta.py`              | Skip already processed PDFs           |
| `ocr_text_extractor.py` | OCR logic for scanned PDFs            |

---

## 🐞 Troubleshooting

| Problem           | Solution                                 |
| ----------------- | ---------------------------------------- |
| OCR fails         | Ensure `tesseract-ocr-san` is installed  |
| PDF not processed | Check `poppler-utils` is installed       |
| Downloads hang    | Increase request timeout in `crawler.py` |
| Missing metadata  | Review PDF structure or fallback logic   |

---

## 📁 Project Structure

```
sanskrit-doc-harvester/
├── crawler.py              # Web crawler logic
├── main.py                 # Pipeline entrypoint
├── processor.py            # Text + metadata extraction
├── text_extractor.py       # Text extraction logic
├── metadata_extractor.py   # Title, author, year parser
├── delta.py                # Change detection
├── utils.py                # Helper functions
├── requirements.txt        # Python dependencies
└── README.md
```


