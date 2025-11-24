# crawl_data

Data crawling and extraction tools for Vietnamese financial data.

## Features

1. **PDF Text Extraction** (`extract.py`) - Extract and process table data from PDF files using OCR
2. **SBV Exchange Rate Crawler** (`scrapers/sbv/sbv_crawler.py`) - Crawl exchange rate data from State Bank of Vietnam website

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### SBV Exchange Rate Crawler

Run the State Bank of Vietnam exchange rate crawler:

```bash
python run_sbv_crawler.py
```

This will:
- Navigate to the SBV exchange rate data portal
- Set date range from 1 year ago to today
- Extract all available exchange rate data
- Click through detailed views to get comprehensive data
- Save results as HTML file in `craw_html/sbv/` directory

### PDF Text Extraction

Extract text from PDF files:

```bash
python extract.py
```

## Output

- SBV data: `craw_html/sbv/ty_gia_sbv_YYYYMMDD.html`
- PDF extraction: Console output with DataFrame

## Dependencies

- selenium: Web scraping automation
- webdriver-manager: Automatic Chrome driver management
- pdf2image: PDF to image conversion
- easyocr: Optical character recognition
- pandas: Data manipulation
- numpy: Numerical processing