# crawl_data

Data extraction tools for Vietnamese Ministry of Finance (MOF) website.

## Overview

This repository contains tools to extract data from the Vietnamese Ministry of Finance website, specifically from PDF viewers containing debt bulletin information.

## Features

- Extracts data from MOF website PDF viewers using Selenium WebDriver
- Processes the following tables:
  - Mẫu biểu công bố thông tin số 4.02
  - Mẫu biểu công khai thông tin số 4.03  
  - Mẫu biểu công bố thông tin số 4.04
  - Mẫu biểu công bố thông tin số 4.05
  - Mẫu biểu công bố thông tin số 4.06
- Exports data to Excel or CSV formats
- Handles Vietnamese text and complex table structures

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Chrome/Chromium browser is installed on your system.

## Usage

### Basic Usage

```python
from mof_extractor import MOFDataExtractor

# Extract all tables using context manager
with MOFDataExtractor(headless=True) as extractor:
    url = "https://mof.gov.vn/bo-tai-chinh/ban-tin-no-cong/mofucm304557"
    data = extractor.extract_all_tables(url)
    extractor.save_results(data, 'excel')
```

### Command Line

```bash
# Run the main extractor
python mof_extractor.py

# Run example usage
python example_usage.py

# Run tests
python test_extractor.py
```

## Files

- `mof_extractor.py` - Main extraction script with MOFDataExtractor class
- `example_usage.py` - Example usage demonstration
- `test_extractor.py` - Test suite for validation
- `extract.py` - Legacy PDF extraction using OCR
- `Quyen.ipynb` - Research notebook with development code
- `requirements.txt` - Python dependencies

## Technical Details

The extractor works by:
1. Using Selenium WebDriver to navigate to the MOF website
2. Finding the PDF viewer element (`<div id="viewer" class="pdfViewer">`)
3. Scrolling through pages to locate target tables
4. Extracting text coordinates from span elements
5. Processing coordinates to reconstruct table structure
6. Converting to pandas DataFrames and exporting

## Dependencies

- selenium >= 4.0.0
- webdriver-manager >= 3.8.0  
- pandas >= 1.3.0
- numpy >= 1.21.0
- openpyxl >= 3.0.0

## License

This project is for educational and research purposes.