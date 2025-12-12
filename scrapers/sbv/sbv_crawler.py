import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pathlib import Path
from datetime import datetime, timedelta
import time
from modules.common.browser import init_driver

def run():
    """
    Scrape exchange rate data from State Bank of Vietnam website
    """
    driver, wait = init_driver()
    
    try:
        # Navigate to the SBV website
        URL = "https://dttktt.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/tk/ccttqt"
        driver.get(URL)
        
        # Wait for page to load
        time.sleep(5)
        
        # Calculate dates: from 1 year ago to today
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        
        # Format dates as dd/mm/yyyy
        from_date = one_year_ago.strftime('%d/%m/%Y')
        to_date = today.strftime('%d/%m/%Y')
        
        print(f"Searching data from {from_date} to {to_date}")
        
        # Fill in the date inputs
        try:
            # From date input
            from_date_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="T:oc_7650641436region:id1::content"]'))
            )
            from_date_element.clear()
            from_date_element.send_keys(from_date)
            
            # To date input
            to_date_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="T:oc_7650641436region:id4::content"]'))
            )
            to_date_element.clear()
            to_date_element.send_keys(to_date)
            
            # Click search button
            search_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="T:oc_7650641436region:cb1"]'))
            )
            search_button.click()
            
            # Wait for results to load
            time.sleep(5)
            
            # Get the data table
            data_table_element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="T:oc_7650641436region:j_id__ctru26pc9"]/div[1]'))
            )
            
            print("Data table found, proceeding to extract detailed data...")
            
            # Find all "Xem" (View) links
            view_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'x2fe') and text()='Xem']")
            
            all_data_html = []
            
            for i, link in enumerate(view_links):
                try:
                    print(f"Processing view link {i+1}/{len(view_links)}")
                    
                    # Click on the view link
                    driver.execute_script("arguments[0].click();", link)
                    
                    # Wait for detailed data to load
                    time.sleep(3)
                    
                    # Extract detailed data table
                    detailed_table = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="T:oc_7650641436region:j_id__ctru7pc9"]/table/tbody/tr/td[2]/table'))
                    )
                    
                    # Get the HTML of the detailed table
                    table_html = detailed_table.get_attribute('outerHTML')
                    all_data_html.append(f"<h2>Dữ liệu lần {i+1}</h2>\n{table_html}")
                    
                    # Go back using the back button
                    back_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="T:oc_7650641436region:j_id__ctru11pc9"]'))
                    )
                    back_button.click()
                    
                    # Wait for page to return to main view
                    time.sleep(3)
                    
                    # Re-find the view links as DOM might have changed
                    view_links = driver.find_elements(By.XPATH, "//a[contains(@class, 'x2fe') and text()='Xem']")
                    
                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Error processing view link {i+1}: {e}")
                    continue
            
            # Create the complete HTML document
            full_html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Dữ liệu tỷ giá SBV</title>
            </head>
            <body>
                <h1>Dữ liệu tỷ giá Ngân hàng Nhà nước Việt Nam</h1>
                <p>Thời gian truy xuất: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p>Khoảng thời gian dữ liệu: {from_date} - {to_date}</p>
                {''.join(all_data_html)}
            </body>
            </html>
            """
            
            # Save to file
            current_folder = Path(__file__).resolve().parent.name
            output_dir = Path(__file__).resolve().parents[2] / 'craw_html' / current_folder
            output_dir.mkdir(parents=True, exist_ok=True)
            
            today_str = datetime.today().strftime('%Y%m%d')
            output_file = output_dir / f'ty_gia_sbv_{today_str}.html'
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_html)
            
            print(f"Data saved to: {output_file}")
            return URL
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error during data extraction: {e}")
            return None
            
    except Exception as e:
        print(f"General error: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    run()