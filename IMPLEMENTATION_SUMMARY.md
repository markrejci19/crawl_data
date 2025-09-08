# SBV Exchange Rate Crawler - Implementation Summary

## Overview
Successfully implemented a comprehensive web crawler for extracting exchange rate data from the State Bank of Vietnam (SBV) website, based on the provided Vietcombank template.

## Key Features Implemented

### 1. Modular Architecture
- Created `modules/common/browser.py` for reusable Selenium WebDriver initialization
- Proper Python package structure with `__init__.py` files
- Clean separation of concerns

### 2. Date Range Automation
- Automatically calculates date range from 1 year ago to today
- Formats dates in Vietnamese standard format (dd/mm/yyyy)
- Dynamic date calculation ensures always-current data retrieval

### 3. Comprehensive Data Extraction
- Navigates to SBV exchange rate portal: `https://dttktt.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/tk/ccttqt`
- Fills date input fields automatically
- Clicks search button and waits for results
- Identifies and processes all "Xem" (View) links
- Extracts detailed data from each view
- Implements back navigation to process multiple entries

### 4. Robust Error Handling
- Timeout exception handling for slow-loading pages
- Element not found exception handling
- Graceful degradation when individual links fail
- Comprehensive logging for debugging

### 5. HTML Output Generation
- Creates properly formatted HTML documents
- Includes metadata (extraction time, date range)
- Organizes multiple data extractions with headers
- Saves to organized directory structure: `craw_html/sbv/`

## Technical Implementation

### Browser Configuration
- Headless Chrome for server environments
- Optimized window size and user agent
- Disabled GPU and sandbox for compatibility
- 30-second timeout for reliable operation

### XPath Selectors Used
- Date inputs: `//*[@id="T:oc_7650641436region:id1::content"]` and `//*[@id="T:oc_7650641436region:id4::content"]`
- Search button: `//*[@id="T:oc_7650641436region:cb1"]`
- Results table: `//*[@id="T:oc_7650641436region:j_id__ctru26pc9"]/div[1]`
- View links: `//a[contains(@class, 'x2fe') and text()='Xem']`
- Detail table: `//*[@id="T:oc_7650641436region:j_id__ctru7pc9"]/table/tbody/tr/td[2]/table`
- Back button: `//*[@id="T:oc_7650641436region:j_id__ctru11pc9"]`

### File Structure
```
.
├── modules/
│   ├── __init__.py
│   └── common/
│       ├── __init__.py
│       └── browser.py
├── scrapers/
│   └── sbv/
│       └── sbv_crawler.py
├── run_sbv_crawler.py
├── test_structure.py
├── test_logic.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Usage Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Crawler:**
   ```bash
   python run_sbv_crawler.py
   ```

3. **Output Location:**
   - HTML files saved to: `craw_html/sbv/ty_gia_sbv_YYYYMMDD.html`

## Testing
- Structure validation: `python test_structure.py`
- Logic validation: `python test_logic.py`
- Both tests pass successfully

## Dependencies
- selenium: Web automation
- webdriver-manager: Automatic driver management
- Python 3.6+ with pathlib and datetime (built-in)

## Notes
The implementation closely follows the original Vietcombank template pattern while adapting to the specific requirements of the SBV website. The crawler is production-ready and includes comprehensive error handling for reliable operation.