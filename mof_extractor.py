#!/usr/bin/env python3
"""
MOF Data Extractor

Extracts table data from Vietnamese Ministry of Finance website
https://mof.gov.vn/bo-tai-chinh/ban-tin-no-cong/mofucm304557

This script extracts the following tables from the PDF viewer:
- Mẫu biểu công bố thông tin số 4.02
- Mẫu biểu công khai thông tin số 4.03  
- Mẫu biểu công bố thông tin số 4.04
- Mẫu biểu công bố thông tin số 4.05
- Mẫu biểu công bố thông tin số 4.06
"""

import time
import re
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import warnings

warnings.filterwarnings('ignore')


class MOFDataExtractor:
    """Extracts data from MOF website PDF viewer"""
    
    def __init__(self, headless=True):
        """Initialize the extractor with Chrome options"""
        self.driver = None
        self.headless = headless
        self.target_tables = [
            'Mẫu biểu công bố thông tin số 4.02',
            'Mẫu biểu công khai thông tin số 4.03',
            'Mẫu biểu công bố thông tin số 4.04',
            'Mẫu biểu công bố thông tin số 4.05',
            'Mẫu biểu công bố thông tin số 4.06'
        ]
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if self.headless:
            options.add_argument('--headless')
            
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
    def scroll_until_found(self, xpath, container_id="viewerContainer", step=400, max_scroll=50):
        """Scroll through PDF viewer until target element is found"""
        try:
            container = self.driver.find_element(By.ID, container_id)
        except NoSuchElementException:
            print(f"Container {container_id} not found")
            return None
            
        for i in range(max_scroll):
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                return element
            except NoSuchElementException:
                # Scroll down
                self.driver.execute_script("arguments[0].scrollTop += arguments[1];", container, step)
                time.sleep(0.3)  # Wait for text to render
        return None

    def process_adjacent_coordinates(self, input_list):
        """Process coordinates to group adjacent text elements"""
        result = []
        i = 0
        
        while i < len(input_list) - 1:
            x1, y1, value1 = input_list[i]
            x2, y2, value2 = input_list[i + 1]

            if x1 == x2:
                avg_y = (y1 + y2) / 2
                concatenated_values = value1 + " " + value2
                result.append([x1, avg_y, concatenated_values])
                i += 2  # Skip the next element since it has already been processed
            else:
                result.append([x1, y1, value1])  # If no pair, keep the current item in result
                i += 1  # Move to the next element
        
        # If the last element wasn't processed, add it to the result
        if i < len(input_list):
            result.append(input_list[i])

        return result

    def process_adjacent_coordinates2(self, input_list):
        """Alternative processing method for grouping coordinates by y-position"""
        result = []
        i = 0
        
        while i < len(input_list) - 1:
            # Initialize group data for current row
            x1, y1, value1 = input_list[i]
            group_x_sum = x1
            group_values = [value1]
            count = 1
            i += 1
            
            # Start grouping consecutive items with the same y-coordinate
            while i < len(input_list) and input_list[i][1] == y1:
                group_x_sum += input_list[i][0]
                group_values.append(input_list[i][2])
                count += 1
                i += 1

            # Calculate average x and concatenate all values for the group
            avg_x = group_x_sum / count
            concatenated_values = " ".join(group_values)

            # Add the processed group to the result list
            result.append([avg_x, y1, concatenated_values])

        # If the last element wasn't processed, add it to the result
        if i < len(input_list):
            result.append(input_list[i])

        return result

    def clean_lists(self, input_list):
        """Clean lists by removing items matching pattern (digits in parentheses)"""
        cleaned_list = []
        pattern = r'\((\d{1,2})\)'

        for sublist in input_list:
            if len(sublist) >= 5:
                cleaned_sublist = [item for item in sublist if not re.fullmatch(pattern, str(item))]
                cleaned_list.append(cleaned_sublist)

        return cleaned_list

    def extract_table_from_page(self, table_name, processing_method="method1"):
        """Extract table data from a specific page"""
        print(f"\nSearching for: {table_name}")
        
        target_xpath = f"//span[contains(text(), '{table_name}')]"
        target = self.scroll_until_found(target_xpath)

        if not target:
            print(f"Table '{table_name}' not found")
            return None

        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", target)
            print(f"Found: {target.text}")
        except Exception as e:
            print(f"Error scrolling to target: {e}")
            return None

        try:
            page_div = target.find_element(By.XPATH, "./ancestor::div[contains(@class,'page')]")
            page_number = page_div.get_attribute("data-page-number")
            print(f"Table is on page: {page_number}")
        except Exception as e:
            print(f"Error finding page number: {e}")
            return None

        try:
            page = self.driver.find_element(By.XPATH, f"//div[@class='page' and @data-page-number='{page_number}']")
            spans = page.find_elements(By.CSS_SELECTOR, ".textLayer span")
        except Exception as e:
            print(f"Error finding page spans: {e}")
            return None

        # Extract text and coordinates
        rows = []
        for span in spans:
            text = span.text.strip()
            
            if not text or text == 'Trong đó:':
                continue
                
            style = span.get_attribute("style")
            left_val = None
            top_val = None
            
            for part in style.split(";"):
                if "left:" in part:
                    left_val = float(part.replace("left:", "").replace("px", "").strip())
                if "top:" in part:
                    top_val = float(part.replace("top:", "").replace("px", "").strip())
            
            if left_val is not None and top_val is not None:
                if processing_method == "method1":
                    rows.append((top_val, left_val, text))
                else:
                    rows.append((left_val, top_val, text))

        if not rows:
            print("No data extracted from page")
            return None

        # Process coordinates based on method
        if processing_method == "method1":
            processed_rows = self.process_adjacent_coordinates2(rows)
            lines = {}
            for top, left, txt in processed_rows:
                key = round(top, 0)
                lines.setdefault(key, []).append(txt)
            sorted_lines = [lines[k] for k in sorted(lines.keys())]
        else:
            processed_rows = self.process_adjacent_coordinates(rows)
            lines = {}
            for left, top, txt in processed_rows:
                key = round(left, 0)
                lines.setdefault(key, []).append(txt)
            sorted_lines = [lines[k] for k in sorted(lines.keys())]

        # Clean and format the data
        table_lines = self.clean_lists(sorted_lines)
        
        if not table_lines:
            print("No table data after cleaning")
            return None

        # Special formatting for certain tables
        if processing_method == "method2":
            if len(table_lines) > 0:
                table_lines[0] = [item for item in table_lines[0] for _ in range(2)]
                table_lines[0].insert(0, 'Year')
            if len(table_lines) > 1:
                table_lines[1].insert(0, 'Currency')

        return pd.DataFrame(table_lines[1:], columns=table_lines[0]) if len(table_lines) > 1 else None

    def extract_all_tables(self, url):
        """Extract all target tables from the MOF website"""
        print(f"Navigating to: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
        except Exception as e:
            print(f"Error loading page: {e}")
            return {}

        extracted_data = {}

        for i, table_name in enumerate(self.target_tables):
            # Use different processing method for table 4.06
            method = "method2" if table_name.endswith("4.06") else "method1"
            
            try:
                df = self.extract_table_from_page(table_name, processing_method=method)
                if df is not None:
                    extracted_data[table_name] = df
                    print(f"Successfully extracted {table_name} with {len(df)} rows")
                else:
                    print(f"Failed to extract {table_name}")
            except Exception as e:
                print(f"Error extracting {table_name}: {e}")

        return extracted_data

    def save_results(self, data, output_format='excel'):
        """Save extracted data to file"""
        if not data:
            print("No data to save")
            return

        if output_format.lower() == 'excel':
            filename = f"mof_extracted_data_{int(time.time())}.xlsx"
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for table_name, df in data.items():
                    # Clean sheet name (Excel has character limits)
                    sheet_name = table_name.replace('Mẫu biểu công bố thông tin số ', 'Table_')
                    sheet_name = sheet_name.replace('Mẫu biểu công khai thông tin số ', 'Public_Table_')
                    sheet_name = sheet_name[:31]  # Excel sheet name limit
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Data saved to {filename}")
        else:
            # Save as CSV files
            for table_name, df in data.items():
                filename = f"{table_name.replace(' ', '_').replace('số_', '')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"Saved {filename}")

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def main():
    """Main execution function"""
    url = "https://mof.gov.vn/bo-tai-chinh/ban-tin-no-cong/mofucm304557"
    
    print("MOF Data Extractor Starting...")
    print("=" * 50)
    
    try:
        with MOFDataExtractor(headless=False) as extractor:
            # Extract all tables
            data = extractor.extract_all_tables(url)
            
            # Print summary
            print("\n" + "=" * 50)
            print("EXTRACTION SUMMARY")
            print("=" * 50)
            
            for table_name, df in data.items():
                print(f"\n{table_name}:")
                print(f"  Rows: {len(df)}")
                print(f"  Columns: {len(df.columns)}")
                print(f"  Column names: {list(df.columns)}")
                
                # Show first few rows
                print("\n  Sample data:")
                print(df.head(3).to_string(max_cols=5))
            
            # Save results
            if data:
                extractor.save_results(data, 'excel')
                print(f"\nSuccessfully extracted {len(data)} tables")
            else:
                print("\nNo tables were extracted")
                
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()